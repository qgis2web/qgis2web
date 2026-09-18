import os
import platform
import functools
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote

from qgis.core import QgsApplication
from qgis.PyQt.QtCore import QLibraryInfo, QSettings, QUrl, QT_VERSION_STR, Qt
from qgis.PyQt.QtGui import QSurfaceFormat
from qgis.PyQt.QtWidgets import QVBoxLayout, QWidget


QML_FILE = os.path.join(
    os.path.dirname(__file__),
    "browser_qt6.qml" if QT_VERSION_STR.startswith("6") else "browser.qml",
)

PREVIEW_INITIAL_WIDTH = 500
PREVIEW_INITIAL_HEIGHT = 500


class _PreviewRequestHandler(SimpleHTTPRequestHandler):
    def log_message(self, format_string, *args):
        return


# Environment entries that previous plugin versions wrote into the global
# QGIS settings (qgis/customEnvVars). They force Chromium flags
# (--single-process, --disable-gpu, --disable-software-rasterizer) that are a
# known cause of blank previews inside QGIS, so they are removed on load.
_OLD_BAD_WE_ENTRIES = {
    "QTWEBENGINE_CHROMIUM_FLAGS": (
        "--no-sandbox --disable-gpu --disable-dev-shm-usage "
        "--disable-software-rasterizer --disable-background-timer-throttling "
        "--disable-backgrounding-occluded-windows --disable-renderer-backgrounding "
        "--disable-features=TranslateUI --single-process"
    ),
    "QTWEBENGINE_DISABLE_SANDBOX": "1",
    "QT_LOGGING_RULES": "qt.webenginecontext.debug=false",
    "QTWEBENGINE_REMOTE_DEBUGGING": "0",
}
_UNSAFE_CHROMIUM_FLAGS = {
    "--single-process",
    "--disable-gpu",
    "--disable-software-rasterizer",
}


def cleanup_polluted_webengine_settings():
    """Remove the QtWebEngine variables that previous plugin versions wrote
    into the user's QGIS environment settings (qgis/customEnvVars)."""
    try:
        settings = QSettings()
        entries = settings.value("qgis/customEnvVars", [], type=list) or []
        kept = []
        for entry in entries:
            if "|" not in entry or "=" not in entry:
                kept.append(entry)
                continue
            prefix, _, key_value = entry.partition("|")
            key, _, value = key_value.partition("=")
            if key == "QTWEBENGINE_CHROMIUM_FLAGS":
                safe_flags = " ".join(
                    flag for flag in value.split()
                    if flag not in _UNSAFE_CHROMIUM_FLAGS
                )
                if safe_flags:
                    kept.append(f"{prefix}|{key}={safe_flags}")
                continue
            if key in _OLD_BAD_WE_ENTRIES and value == _OLD_BAD_WE_ENTRIES[key]:
                continue
            kept.append(entry)
        if len(kept) != len(entries):
            settings.setValue("qgis/customEnvVars", kept)
        current_flags = os.environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        safe_flags = " ".join(
            flag for flag in current_flags.split()
            if flag not in _UNSAFE_CHROMIUM_FLAGS
        )
        if safe_flags:
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = safe_flags
        else:
            os.environ.pop("QTWEBENGINE_CHROMIUM_FLAGS", None)
    except Exception:
        pass


def _apply_webengine_env():
    """Set minimal, platform-appropriate QtWebEngine environment variables.

    These affect only the current QGIS process and are never written into the
    user's QGIS settings. Forcing Chromium flags such as --single-process,
    --disable-gpu or --disable-software-rasterizer is a known cause of blank
    previews (Chromium is left without a rendering backend), so they are no
    longer set by default.
    """
    if platform.system() in ("Darwin", "Linux"):
        # The WebEngine sandbox helper frequently fails on macOS QGIS (blank
        # preview); the Chromium sandbox often cannot start inside QGIS on
        # Linux. Windows does not need this.
        os.environ.setdefault("QTWEBENGINE_DISABLE_SANDBOX", "1")
    os.environ.setdefault("QML_USE_GLYPHCACHE_WORKAROUND", "1")
    if os.environ.get("QGIS2WEB_DEBUG_PREVIEW") or os.environ.get("QGIS2OGIS_DEBUG_PREVIEW"):
        # Optional debugging: open http://localhost:9222 in a web browser to
        # inspect the preview page, and send Chromium logs to the console.
        os.environ.setdefault("QTWEBENGINE_REMOTE_DEBUGGING", "9222")
        os.environ.setdefault(
            "QTWEBENGINE_CHROMIUM_FLAGS",
            "--enable-logging --log-level=0 --v=1",
        )


def _qt_qml_path():
    try:
        return QLibraryInfo.path(QLibraryInfo.LibraryPath.Qml2ImportsPath)
    except AttributeError:
        try:
            return QLibraryInfo.location(QLibraryInfo.Qml2ImportsPath)
        except AttributeError:
            return ""


def _qt_library_path():
    """Return the Qt library path (QtHome on macOS) or an empty string."""
    getter = getattr(QgsApplication, "qtLibraryPath", None)
    if not callable(getter):
        getter = getattr(QgsApplication, "libraryPath", None)
    if callable(getter):
        try:
            value = getter()
            return str(value) if value else ""
        except Exception:
            return ""
    return ""


def _qml_import_paths():
    prefix = QgsApplication.prefixPath()
    libexec = QgsApplication.libexecPath()
    qt_lib = _qt_library_path()
    qt6 = QT_VERSION_STR.startswith("6")
    qt_name = "Qt6" if qt6 else "Qt5"
    qt_lower_name = qt_name.lower()
    candidates = [_qt_qml_path()]
    if qt_lib:
        candidates = [
            os.path.join(qt_lib, "qml"),
            os.path.join(qt_lib, "Qt", "qml"),
            os.path.join(qt_lib, qt_name, "qml"),
        ] + candidates
    candidates += [
        os.path.join(prefix, "qml"),
        os.path.join(prefix, qt_name, "qml"),
        os.path.join(prefix, qt_lower_name, "qml"),
        os.path.join(prefix, "apps", qt_name, "qml"),
        os.path.join(prefix, "..", qt_name, "qml"),
        os.path.join(prefix, "..", qt_lower_name, "qml"),
        os.path.join(prefix, "..", "apps", qt_name, "qml"),
        # macOS QGIS.app bundle
        os.path.join(prefix, "..", "..", "Frameworks", "Qt", "qml"),
        os.path.join(prefix, "..", "..", "Frameworks", qt_name, "qml"),
        os.path.join(prefix, "..", "..", "Frameworks", qt_lower_name, "qml"),
        os.path.join(libexec, "..", "Frameworks", "Qt", "qml"),
        os.path.join(libexec, "..", "Frameworks", qt_name, "qml"),
        os.path.join(libexec, "..", "Frameworks", qt_lower_name, "qml"),
        os.path.join(libexec, "..", qt_name, "qml"),
        os.path.join(libexec, "..", qt_lower_name, "qml"),
    ]
    paths = list(dict.fromkeys(
        os.path.normpath(path) for path in candidates
        if path and os.path.isdir(path)
    ))
    # Fallback: locate any Qt "qml" directory containing the QtWebEngine module
    if not any(os.path.isdir(os.path.join(path, "QtWebEngine")) for path in paths):
        for root in (
            qt_lib,
            os.path.join(prefix, "..", "..", "Frameworks"),
            os.path.join(libexec, "..", "Frameworks"),
            os.path.join(prefix, ".."),
            libexec,
        ):
            if not root or not os.path.isdir(root):
                continue
            try:
                entries = os.listdir(root)
            except OSError:
                continue
            for name in entries:
                if name.lower() not in ("qt", qt_lower_name):
                    continue
                qml_dir = os.path.join(root, name, "qml")
                if os.path.isdir(os.path.join(qml_dir, "QtWebEngine")):
                    paths.append(os.path.normpath(qml_dir))
    return list(dict.fromkeys(paths))


class LocalPreviewServer:
    """Serve one exported map directory over loopback HTTP."""

    def __init__(self, thread_name="qgis-preview-server"):
        self._server = None
        self._thread = None
        self._thread_name = thread_name

    def start(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(file_path)
        self.stop()
        preview_dir = os.path.dirname(os.path.abspath(file_path))
        preview_name = os.path.basename(file_path)
        handler = functools.partial(_PreviewRequestHandler, directory=preview_dir)
        self._server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self._server.daemon_threads = True
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name=self._thread_name,
            daemon=True,
        )
        self._thread.start()
        port = self._server.server_address[1]
        return QUrl(f"http://127.0.0.1:{port}/{quote(preview_name)}")

    def stop(self):
        server = self._server
        thread = self._thread
        self._server = None
        self._thread = None
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None:
            thread.join(timeout=1.0)




class QmlPreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        _apply_webengine_env()
        # Do not force the Qt Quick software scene graph here: Qt only allows one
        # graphics API per top-level window, and MainDialog hosts other
        # OpenGL-backed widgets (e.g. QgsColorButton). Forcing software mode
        # conflicts with them and can blank the whole dialog.
        if platform.system() == "Windows" and not QT_VERSION_STR.startswith("6"):
            # Reset the default surface format (Qt5): helps on Windows RDP and
            # virtual machines, where the scene graph otherwise picks an
            # incompatible OpenGL context.
            QSurfaceFormat.setDefaultFormat(QSurfaceFormat())
        self.view = None
        self.container = None
        self._preview_server = None
        self._preview_thread = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(PREVIEW_INITIAL_WIDTH, PREVIEW_INITIAL_HEIGHT)

    def _create_view(self, url):
        if QT_VERSION_STR.startswith("6"):
            try:
                from qgis.PyQt import QtWebEngineQuick
                QtWebEngineQuick.initialize()
            except Exception:
                pass
        if QT_VERSION_STR.startswith("6"):
            try:
                from qgis.PyQt.QtQuickWidgets import QQuickWidget
            except ImportError:
                from PyQt6.QtQuickWidgets import QQuickWidget
            self.view = QQuickWidget(self)
            self.view.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
            self.container = self.view
        else:
            try:
                from qgis.PyQt.QtQuick import QQuickView
            except ImportError:
                from PyQt5.QtQuick import QQuickView
            self.view = QQuickView()
            self.view.setResizeMode(QQuickView.ResizeMode.SizeRootObjectToView)
            self.container = QWidget.createWindowContainer(self.view, self)
            focus_policy = getattr(Qt, "FocusPolicy", Qt)
            self.container.setFocusPolicy(focus_policy.StrongFocus)
        self.layout().addWidget(self.container)
        for path in _qml_import_paths():
            self.view.engine().addImportPath(path)
        self.view.resize(PREVIEW_INITIAL_WIDTH, PREVIEW_INITIAL_HEIGHT)
        qml_file = QML_FILE
        alternate_qml = os.path.join(
            os.path.dirname(__file__),
            "browser.qml" if QT_VERSION_STR.startswith("6") else "browser_qt6.qml",
        )
        if QT_VERSION_STR.startswith("6"):
            self.view.setSource(QUrl.fromLocalFile(qml_file))
        else:
            getattr(self.view, "setInitialProperties")({"sourceUrl": url})
            self.view.setSource(QUrl.fromLocalFile(qml_file))
        status_type = type(self.view).Status
        if self.view.status() == status_type.Error:
            errors = "\n".join(error.toString() for error in self.view.errors())
            # Retry with the alternate QtWebEngine QML version when the module is missing
            if "not installed" in errors and os.path.exists(alternate_qml):
                self.view.setSource(QUrl.fromLocalFile(alternate_qml))
        if self.view.status() == status_type.Error:
            errors = "\n".join(error.toString() for error in self.view.errors())
            self.view = None
            raise RuntimeError(errors or "Unable to load the local QtWebEngine component")
        if QT_VERSION_STR.startswith("6"):
            root = self.view.rootObject()
            if root is None:
                self.view = None
                raise RuntimeError("The local QtWebEngine QML component has no root object")
            root.setProperty("sourceUrl", url)
        self.container.show()

    def _start_preview_server(self, file_path):
        if self._preview_server is None:
            self._preview_server = LocalPreviewServer()
        return self._preview_server.start(file_path)

    def _stop_preview_server(self):
        if self._preview_server is not None:
            self._preview_server.stop()

    def stop_server(self):
        self._stop_preview_server()

    def set_url(self, file_path):
        self._stop_preview_server()
        url = self._start_preview_server(file_path)
        print(f"Preview server URL: {url.toString()}")
        if self.view is None:
            try:
                self._create_view(url)
            except Exception:
                self._stop_preview_server()
                raise
        else:
            root = self.view.rootObject()
            if root is None:
                self._stop_preview_server()
                raise RuntimeError("The local QtWebEngine QML component has no root object")
            root.setProperty("sourceUrl", url)

    def closeEvent(self, event):
        self._stop_preview_server()
        if self.view is not None:
            if QT_VERSION_STR.startswith("6"):
                self.view.deleteLater()
            else:
                self.view.close()
        super().closeEvent(event)

    def set_html(self, html):
        if self.view is None:
            self._create_view(QUrl())
        root = self.view.rootObject()
        if root is None:
            raise RuntimeError("The local QtWebEngine QML component has no root object")
        root.setProperty("htmlContent", html)
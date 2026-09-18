import QtQuick 2.15
import QtQuick.Window 2.15
import QtQml 2.15
import QtWebEngine 2

Item {
    id: root
    property url sourceUrl: ""
    property string htmlContent: ""

    property WebEngineView webView: null

    function init_config(web_profile, web_settings) {
        web_settings.javascriptEnabled = true
    }

    Component {
        id: webViewComponent

        WebEngineView {
            anchors.fill: parent
            settings.javascriptEnabled: true
            settings.localContentCanAccessFileUrls: true
            settings.localContentCanAccessRemoteUrls: true

            onLoadingChanged: function(loadRequest) {
                if (loadRequest.status === WebEngineView.LoadFailedStatus)
                    console.error("Preview load failed: " + loadRequest.errorString)
            }
        }
    }

    Component.onCompleted: {
        init_config(WebEngine.defaultProfile, WebEngine.settings)
        webView = webViewComponent.createObject(root, {"url": sourceUrl})
    }

    onSourceUrlChanged: {
        if (webView)
            webView.url = sourceUrl
    }
    onHtmlContentChanged: {
        if (webView && htmlContent !== "")
            webView.setHtml(htmlContent)
    }
}
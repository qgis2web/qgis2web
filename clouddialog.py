# -*- coding: utf-8 -*-

# Copyright (C) 2026 Andrea Ordonselli
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Dialog of "Cloud Export" and "Cloud Update".

The dialog does not contain any rule of its own: it asks the site for the publishing
policy and shows what the site answers. The instructions and the confirmations the user
sees here are the same texts shown by the manual upload page of the site, so updating
the site updates the plugin as well.

Only the site address, the user name and the name of the published project are kept in
the QGIS project. The password (or application password) is stored in the QGIS
authentication database, and the project keeps just the identifier of that entry: a
project sent to somebody else brings the address but no secret.
"""

from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                                 QFormLayout, QFrame, QGroupBox, QHBoxLayout, QLabel,
                                 QLineEdit, QMessageBox, QPushButton, QScrollArea,
                                 QVBoxLayout, QWidget)

from .cloudapi import (DEFAULT_SITE_URL, CloudClient, CloudError,
                       allow_dev_site, is_default_site, normalize_site_url,
                       site_root_url)
from .cloudzip import normalize_slug

#: Membership (monthly contribution) checkout link, shown to non-member accounts.
MEMBERSHIP_LINK = 'https://buy.stripe.com/aFaaEY7YK1CNeV82j7cwg04'


def api_base_url(site_url):
    return site_root_url(site_url).rstrip('/') + '/wp-json/ogis/v1'


def auth_manager():
    try:
        from qgis.core import QgsApplication
        return QgsApplication.authManager()
    except Exception:
        return None


def slug_from_project(title, fallback='project'):
    return normalize_slug(title) or fallback


def format_size(num_bytes):
    """Human readable size, used for the quota and the archive."""
    try:
        num_bytes = float(num_bytes)
    except (TypeError, ValueError):
        return '-'
    if num_bytes >= 1024 * 1024 * 1024:
        return '{:.2f} GB'.format(num_bytes / (1024 * 1024 * 1024))
    if num_bytes >= 1024 * 1024:
        return '{:.1f} MB'.format(num_bytes / (1024 * 1024))
    if num_bytes >= 1024:
        return '{:.0f} KB'.format(num_bytes / 1024)
    return '{:.0f} B'.format(num_bytes)


class CloudPublishDialog(QDialog):
    """Collect the destination, the credentials and the confirmations.

    :param mode: ``create`` for "Cloud Export", ``update`` for "Cloud Update"
    :param settings: values remembered in the project (site address, user name,
        credentials identifier, project name)
    """

    def __init__(self, parent=None, mode='create', settings=None):
        QDialog.__init__(self, parent)
        self.mode = 'update' if mode == 'update' else 'create'
        self.settings = dict(settings or {})

        #: filled by the dialog and read back by the caller
        self.site_url = normalize_site_url(
            self.settings.get('site_url') or DEFAULT_SITE_URL)
        self.username = self.settings.get('username') or ''
        self.password = self.settings.get('password') or ''
        self.remember = bool(self.settings.get('remember', True))
        self.slug = self.settings.get('slug') or ''
        self.display_name = self.settings.get('display_name') or ''
        self.target_slug = self.settings.get('target_slug') or ''
        self.linked_project_id = self.settings.get('target_project_id') or ''
        self.target_project_id = ''
        self.consents = []
        self.policy = {}
        self.account = {}
        self.projects = []
        self.consentChecks = []

        self.setMinimumSize(420, 360)
        self.resize(680, 640)
        self.setWindowTitle(self.tr('Cloud Update') if self.mode == 'update'
                            else self.tr('Cloud Export'))
        self._build_ui()
        self._restore_settings()

    # -- user interface ----------------------------------------------------------

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget(scroll)
        layout = QVBoxLayout(content)

        banner = QLabel(self.tr(
            'Cloud publishing is powered by O.GIS Cloud available at <a href="{site}">https://www.opengis.cloud</a>'
        ).format(site=DEFAULT_SITE_URL))
        banner.setWordWrap(True)
        banner.setOpenExternalLinks(True)
        banner.setStyleSheet('font-size: 12px; font-weight: bold; color: #1a5a8f;')
        layout.addWidget(banner)

        legal_root = site_root_url(DEFAULT_SITE_URL)
        legal = QLabel(self.tr(
            '<b>Publishing is free</b>, but it is governed by the site\'s '
            '<a href="{terms}">Terms of Service</a> and <a href="{privacy}">Privacy '
            'Policy</a> &mdash; please read them. Contributors who support the '
            'plugin\'s development get more storage and extra features.'
        ).format(terms=legal_root + '/terms/', privacy=legal_root + '/privacy-policy/'))
        legal.setWordWrap(True)
        legal.setOpenExternalLinks(True)
        legal.setStyleSheet('padding:4px; background:#fff8e1; border:1px solid #ffe082;')
        layout.addWidget(legal)

        tip = QLabel(self.tr(
            'Tip: run a Local Export first and check that the map works exactly as '
            'you expect before publishing it to the cloud.'))
        tip.setWordWrap(True)
        tip.setStyleSheet('color:#666; font-style: italic;')
        layout.addWidget(tip)

        form = QFormLayout()
        # The destination site is fixed. A project received from somebody else must not be
        # able to change it (that is how credentials are stolen), and the same rule keeps
        # the plugin simple: the user never types an address. Only an installation with the
        # development option enabled may point the upload somewhere else.
        self.devSiteCheck = None
        site_row = QHBoxLayout()
        self.siteEdit = QLineEdit(self.site_url)
        self.siteEdit.setReadOnly(True)
        self.siteEdit.setToolTip(self.tr(
            'Address of the site that publishes the maps: {}.').format(
                DEFAULT_SITE_URL))
        site_row.addWidget(self.siteEdit, 1)
        if allow_dev_site():
            self.devSiteCheck = QCheckBox(self.tr('Development site'))
            self.devSiteCheck.setToolTip(self.tr(
                'Unlock the address field to test the upload on a local or test '
                'installation, for example http://localhost/cloud. Publish to a site you '
                'do not control only if you trust it: the credentials are typed by you '
                'and sent there.'))
            self.devSiteCheck.setChecked(not is_default_site(self.site_url))
            self.devSiteCheck.toggled.connect(self._toggle_dev_site)
            site_row.addWidget(self.devSiteCheck)
        form.addRow(self.tr('Site address'), site_row)
        self.apiLabel = QLabel('')
        self.apiLabel.setStyleSheet('color:#666; font-size: 11px;')
        form.addRow('', self.apiLabel)
        self._toggle_dev_site(self.devSiteCheck is not None
                              and self.devSiteCheck.isChecked())
        if self.devSiteCheck is None:
            locked = QLabel(self.tr(
                'The address cannot be changed: projects are published on the official '
                'O.GIS Cloud site.'))
            locked.setWordWrap(True)
            locked.setStyleSheet('color:#666; font-size: 11px;')
            form.addRow('', locked)

        self.userEdit = QLineEdit(self.username)
        self.userEdit.setToolTip(self.tr('User name of the account on the site.'))
        form.addRow(self.tr('Site user name'), self.userEdit)

        password_row = QHBoxLayout()
        self.passwordEdit = QLineEdit(self.password)
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordEdit.setToolTip(self.tr(
            'WordPress account password or Application Password. Public sites require '
            'HTTPS.'))
        password_row.addWidget(self.passwordEdit)
        self.showButton = QPushButton(self.tr('Show'))
        self.showButton.setCheckable(True)
        self.showButton.setMaximumWidth(70)
        self.showButton.toggled.connect(self._toggle_password)
        password_row.addWidget(self.showButton)
        form.addRow(self.tr('Password or key'), password_row)

        self.rememberCheck = QCheckBox(self.tr(
            'Remember the credentials in QGIS (never inside the project file)'))
        self.rememberCheck.setChecked(self.remember)
        if auth_manager() is None:
            self.rememberCheck.setChecked(False)
            self.rememberCheck.setEnabled(False)
            self.rememberCheck.setToolTip(self.tr(
                'The QGIS authentication database is not available, so the credentials '
                'cannot be remembered.'))
        else:
            self.rememberCheck.setToolTip(self.tr(
                'The credentials are saved by QGIS, encrypted with its master password. '
                'The project file only keeps the identifier of that entry, so nobody '
                'receiving the project can read your password.'))
        form.addRow('', self.rememberCheck)
        layout.addLayout(form)

        connect_row = QHBoxLayout()
        self.connectButton = QPushButton(self.tr('Connect and load the rules'))
        self.connectButton.clicked.connect(self.connect_to_site)
        connect_row.addWidget(self.connectButton)
        self.statusLabel = QLabel('')
        self.statusLabel.setWordWrap(True)
        connect_row.addWidget(self.statusLabel, 1)
        layout.addLayout(connect_row)

        self.accountBox = QGroupBox(self.tr('Your plan on the site'))
        account_layout = QVBoxLayout(self.accountBox)
        self.accountDetails = QLabel(self.tr(
            'Connect to see your plan, the space you have used and which features are '
            'available to your account.'))
        self.accountDetails.setWordWrap(True)
        self.accountDetails.setOpenExternalLinks(True)
        account_layout.addWidget(self.accountDetails)
        layout.addWidget(self.accountBox)

        self.consentBox = QGroupBox(self.tr('Confirmations required before publishing'))
        self.consentLayout = QVBoxLayout(self.consentBox)
        self.consentLayout.addWidget(QLabel(self.tr(
            'Connect to the site to load the confirmations required for your account.')))
        layout.addWidget(self.consentBox)

        project_box = QGroupBox(self.tr('Published project'))
        project_box_layout = QVBoxLayout(project_box)
        project_form = QFormLayout()
        # The wrapped info lines (slug preview, project address, note) are added to
        # project_box_layout, not as QFormLayout rows: a word-wrapped QLabel used as a
        # form row reserves the height of its narrow sizeHint, leaving an empty band
        # above the text (Qt computes that hint for a much smaller width).
        project_box_layout.addLayout(project_form)
        self.projectCombo = None
        self.slugEdit = None
        self.slugPreview = None
        self.displayEdit = None
        self.projectInfo = QLabel('')
        self.projectInfo.setStyleSheet('color:#666; font-size: 11px;')
        self.projectInfo.setWordWrap(True)
        if self.mode == 'update':
            self.projectCombo = QComboBox()
            self.projectCombo.currentIndexChanged.connect(self._project_changed)
            project_form.addRow(self.tr('Project on the site'), self.projectCombo)
            project_box_layout.addWidget(self.projectInfo)
            note = QLabel(self.tr(
                'Before sending, the export is compared with the published revision: '
                'you will see how many files are added, updated or removed and you can '
                'still cancel. Password protection, CORS settings and the branding '
                'banner of the project are kept.'))
        else:
            self.slugEdit = QLineEdit(self.slug)
            self.slugEdit.setToolTip(self.tr(
                'Type any name you like: it is simplified automatically into the '
                'web-safe name shown below, which becomes part of the public address.'))
            self.slugEdit.textChanged.connect(self._validate)
            self.slugEdit.textChanged.connect(self._update_slug_preview)
            project_form.addRow(self.tr('Project name'), self.slugEdit)
            self.slugPreview = QLabel('')
            self.slugPreview.setStyleSheet('color:#666; font-size: 11px;')
            self.slugPreview.setWordWrap(True)
            project_box_layout.addWidget(self.slugPreview)
            note = QLabel(self.tr(
                'If a project with this name already exists, you will be asked whether '
                'to update it instead of creating a duplicate.'))
        note.setWordWrap(True)
        note.setStyleSheet('color:#666; font-size: 11px;')
        project_box_layout.addWidget(note)
        layout.addWidget(project_box)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                        QDialogButtonBox.StandardButton.Cancel)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            self.tr('Update project') if self.mode == 'update' else self.tr('Publish'))
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout.addStretch(1)
        scroll.setWidget(content)
        outer.addWidget(scroll)
        outer.addWidget(self.buttons)

        self._update_api_label()
        self.siteEdit.textChanged.connect(self._update_api_label)
        if self.devSiteCheck is not None:
            self.siteEdit.textChanged.connect(self._dev_site_changed)
        self._validate()

    def _toggle_dev_site(self, unlocked):
        """Lock or unlock the address field and keep the displayed address consistent."""
        if self.devSiteCheck is None:
            self.siteEdit.setReadOnly(True)
            return
        self.siteEdit.setReadOnly(not unlocked)
        if not unlocked:
            self.siteEdit.setText(DEFAULT_SITE_URL)
            status = getattr(self, 'statusLabel', None)
            if status is not None:
                status.setText('')
        self._update_api_label()

    def _update_api_label(self):
        label = getattr(self, 'apiLabel', None)
        if label is not None:
            label.setText(self.tr('API used: {}').format(
                api_base_url(self.siteEdit.text())))

    def _toggle_password(self, shown):
        self.passwordEdit.setEchoMode(QLineEdit.EchoMode.Normal if shown
                                      else QLineEdit.EchoMode.Password)
        self.showButton.setText(self.tr('Hide') if shown else self.tr('Show'))

    def _restore_settings(self):
        if self.mode == 'create' and not self.slug and self.slugEdit is not None:
            try:
                from qgis.core import QgsProject
                self.slugEdit.setText(slug_from_project(QgsProject.instance().title()))
            except Exception:
                pass
        self._update_slug_preview()
        if not self._address_locked() and not is_default_site(self.site_url):
            self.statusLabel.setText(self.tr(
                'Development site configured: check the address before publishing.'))
        if self.username and self.password and not self.statusLabel.text():
            # Saved credentials are filled in but never used until the user asks to
            # connect: opening the dialog must not start a session with the site.
            self._set_status(self.tr(
                'Saved credentials loaded: press "Connect and load the rules" to load '
                'your plan and continue.'), False)

    # -- site interaction --------------------------------------------------------

    def client(self):
        # Reading calls are short: a site that does not answer must not freeze the
        # dialog for the (much longer) time allowed to an upload.
        return CloudClient(self.siteEdit.text(), self.userEdit.text(),
                           self.passwordEdit.text(), timeout=45)

    def connect_to_site(self):
        """Load policy, account and (for an update) the published projects."""
        self.connectButton.setEnabled(False)
        self._set_status(self.tr('Connecting to {} ...').format(self.siteEdit.text()), False)
        client = self.client()
        try:
            self.policy = client.policy()
        except CloudError as error:
            self.policy = {}
            self._set_status(error.message, True)
            self.connectButton.setEnabled(True)
            return
        try:
            self.account = client.ping()
        except CloudError as error:
            self.account = {}
            self._set_status(error.message, True)
            self._show_consents()
            self._show_account_details()
            self.connectButton.setEnabled(True)
            self._validate()
            return
        self._show_consents()
        self._show_account_details()
        self._set_status(self._account_summary(), False)

        if self.mode == 'update':
            try:
                self.projects = client.projects()
            except CloudError as error:
                self.projects = []
                self._set_status(error.message, True)
            self._fill_projects()
        self.connectButton.setEnabled(True)
        self.connectButton.setText(self.tr('Reconnect'))
        self._validate()

    def _account_summary(self):
        account = self.account or {}
        user = account.get('user') or {}
        lines = [self.tr('Connected as {} ({}).').format(
            user.get('login', ''), account.get('plan_label', ''))]
        admin_rule = str(account.get('admin_rule', '') or '')
        if admin_rule:
            lines.append(admin_rule)
        if not account.get('can_upload', True):
            lines.append(account.get('upload_blocked_reason', ''))
        return ' '.join(line for line in lines if line)

    def _show_account_details(self):
        """Plan, payment, quota and gated features, as a two-column HTML summary.

        Left column mirrors the "payment" column of the site dashboard table (plan,
        contribution status/date/amount); right column mirrors its "features" column.
        The plugin does not invent anything, it only formats what ``/ping`` returns.
        """
        account = self.account or {}
        if not account:
            self.accountDetails.setText(self.tr(
                'Connect to see your plan, the space you have used and which features '
                'are available to your account.'))
            return
        quota = account.get('quota') or {}
        contribution = account.get('contribution') or {}
        membership_status = account.get('membership_status', 'never')
        membership_features_active = bool(account.get(
            'membership_features_active', membership_status == 'active'))
        membership_features_manageable = bool(account.get(
            'membership_features_manageable', membership_status == 'active'))
        can_upload = bool(account.get('can_upload', True))

        left = ['<b>{}</b>'.format(self._escape(account.get('plan_label', '')))]
        # An administrator rule can keep an account usable even when its Stripe
        # contribution has expired: show it right under the plan label, so the user
        # understands why the site still works despite the "expired" date below.
        admin_rule = str(account.get('admin_rule', '') or '')
        if admin_rule:
            left.append('<span style="color:#1b5e20;font-weight:600;">{}</span>'.format(
                self._escape(admin_rule)))
        contribution_type = contribution.get('type', 'none')
        amount = self.tr('{:.2f} EUR').format(float(contribution.get('amount') or 0))
        if contribution_type in ('membership', 'monthly'):
            if contribution.get('expired'):
                left.append('<span style="color:#b3261e;">{}</span>'.format(self._escape(
                    self.tr('Expired on {}').format(contribution.get('expires_at', '')))))
            else:
                left.append(self.tr('Active (expires on {})').format(
                    contribution.get('expires_at', '')))
            if account.get('membership_cancel_at_period_end') and not contribution.get('expired'):
                left.append(self.tr('Membership renewal cancelled; access remains active until {}.').format(
                    contribution.get('expires_at', '')))
            left.append(self.tr('Last contribution: {} &mdash; {}').format(
                contribution.get('date', ''), amount))
            if account.get('account_state') == 'renewal_grace':
                grace_until = str(account.get('renewal_grace_until') or '')
                left.append(self.tr('Renewal period: uploads are paused{}').format(
                    self.tr(' until {}').format(grace_until) if grace_until else ''))
                left.append(self.tr('Existing projects and Membership features remain active.'))
            elif membership_status == 'expired' and not membership_features_active:
                left.append(self.tr('Membership features are no longer active.'))
        elif contribution_type == 'one_time':
            left.append(self.tr('One-time contribution'))
            left.append(self.tr('Date: {} &mdash; {}').format(contribution.get('date', ''), amount))
        else:
            left.append(self.tr('No contribution yet'))
        left.append('')
        # Two different ceilings, on purpose: the account quota (how much this account
        # may publish in total) and the per-upload limit (how big a single archive may
        # be, set by the server hosting the site - e.g. Apache's post_max_size).
        left.append(self.tr('Max available space: {}').format(format_size(quota.get('max_bytes', 0))))
        left.append(self.tr('{} used of {} ({} max upload)').format(
            format_size(quota.get('used_bytes', 0)), format_size(quota.get('max_bytes', 0)),
            format_size(quota.get('max_upload_bytes', 0))))
        if not membership_features_active:
            left.append('<a href="{}">{}</a>'.format(
                MEMBERSHIP_LINK, self._escape(self.tr(
                    'Become a member to unlock more space and features'))))

        def feature_line(enabled, text):
            mark = '\u2714' if enabled else '\u2716'
            color = '#1b5e20' if enabled else '#999'
            return '<span style="color:{};">{} {}</span>'.format(
                color, mark, self._escape(text))

        right = [
            feature_line(can_upload, self.tr('Publish and update projects')),
            feature_line(membership_features_active, self.tr('Password-protect published projects')),
            feature_line(membership_features_active, self.tr('Disable the O.GIS Cloud branding banner')),
            feature_line(membership_features_active, self.tr('Embed maps on other sites (CORS)')),
            feature_line(membership_features_active, self.tr('Visit statistics of your published projects')),
            feature_line(membership_features_active, self.tr('Permanent links for your published projects')),
        ]
        if membership_features_active and not membership_features_manageable:
            right.append(self.tr('Membership settings are read-only during renewal.'))

        self.accountDetails.setText(
            '<table width="100%"><tr>'
            '<td valign="top" style="padding-right:16px;">{left}</td>'
            '<td valign="top">{right}</td>'
            '</tr></table>'.format(
                left='<br>'.join(line for line in left if line != ''),
                right='<br>'.join(right)))

    def _set_status(self, message, is_error):
        self.statusLabel.setText(message or '')
        self.statusLabel.setStyleSheet('color:#b3261e;' if is_error else 'color:#1b5e20;')

    def _show_consents(self):
        while self.consentLayout.count():
            item = self.consentLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                continue
            child_layout = item.layout()
            if child_layout is not None:
                while child_layout.count():
                    child_item = child_layout.takeAt(0)
                    child_widget = child_item.widget()
                    if child_widget is not None:
                        child_widget.deleteLater()
        self.consentChecks = []

        consents = (self.account or {}).get('consents')
        if consents is None:
            consents = (self.policy or {}).get('consents') or []
        shown = 0
        for consent in consents:
            if not consent.get('required'):
                continue
            # QCheckBox has no word-wrap support: long consent texts are shown in a
            # separate wrapping QLabel next to a plain (unlabeled) checkbox instead.
            text = self._escape(consent.get('label') or '')
            if consent.get('link_url'):
                text = '{} <a href="{}">{}</a>'.format(
                    text, self._escape(consent['link_url']), self._escape(consent['link_url']))
            check = QCheckBox()
            check.stateChanged.connect(self._validate)
            text_label = QLabel(text)
            text_label.setWordWrap(True)
            text_label.setOpenExternalLinks(True)
            text_label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
            row = QHBoxLayout()
            row.addWidget(check, 0)
            row.addWidget(text_label, 1)
            self.consentLayout.addLayout(row)
            self.consentChecks.append((consent.get('key', ''), check))
            shown += 1
        if not shown:
            self.consentLayout.addWidget(QLabel(self.tr(
                'Connect to the site to load the confirmations required for your '
                'account.')))
        self._validate()

    def _fill_projects(self):
        self.projectCombo.blockSignals(True)
        self.projectCombo.clear()
        for project in self.projects:
            label = '{} - {}'.format(project.get('slug', ''),
                                     project.get('display_name', ''))[:120]
            details = []
            if project.get('revision'):
                details.append(self.tr('revision {}').format(project['revision']))
            if project.get('created_at'):
                details.append(self.tr('created {}').format(project['created_at']))
            if project.get('updated_at'):
                details.append(project['updated_at'])
            if project.get('last_source'):
                details.append(self.tr('published from QGIS')
                               if project['last_source'] == 'api'
                               else self.tr('dashboard upload'))
            if project.get('size_bytes'):
                details.append(format_size(project['size_bytes']))
            self.projectCombo.addItem(
                '{} [{}]'.format(label, ' - '.join(str(item) for item in details))
                if details else label,
                project.get('slug', ''))
        self.projectCombo.blockSignals(False)
        if self.target_slug:
            index = self.projectCombo.findData(self.target_slug)
            if index >= 0:
                self.projectCombo.setCurrentIndex(index)
        self._project_changed()

    def _project_changed(self):
        slug = self.projectCombo.currentData() if self.projectCombo is not None else ''
        selected = None
        for project in self.projects:
            if project.get('slug') == slug:
                selected = project
                break
        self.target_project_id = str((selected or {}).get('project_id') or '')
        lines = []
        if selected and selected.get('url'):
            lines.append(self.tr('Address: {}').format(selected['url']))
        if selected and selected.get('revision'):
            lines.append(self.tr('Current revision: {}').format(selected['revision']))
        if selected and self.linked_project_id:
            if self.target_project_id != self.linked_project_id:
                lines.append(self.tr(
                    'Warning: this is not the remote project previously linked to this QGIS project.'))
                self.projectInfo.setStyleSheet('color:#b3261e; font-size: 11px;')
            else:
                self.projectInfo.setStyleSheet('color:#666; font-size: 11px;')
        elif selected:
            lines.append(self.tr(
                'This QGIS project has no saved remote identity yet; confirming will link it to this project.'))
            self.projectInfo.setStyleSheet('color:#8a4b08; font-size: 11px;')
        self.projectInfo.setText('\n'.join(lines))
        self._validate()

    def _update_slug_preview(self):
        """Show, live, the web-safe name typed text will become once published."""
        if self.slugPreview is None or self.slugEdit is None:
            return
        raw = self.slugEdit.text().strip()
        normalized = normalize_slug(raw)
        if not normalized:
            self.slugPreview.setText(self.tr(
                'Type at least one letter or digit: nothing web-safe to publish yet.'))
        elif normalized == raw:
            self.slugPreview.setText(self.tr(
                'This name is already web-safe and becomes part of the public address.'))
        else:
            self.slugPreview.setText(self.tr('Will be published as: {}').format(normalized))

    def _validate(self):
        ready = bool(self.policy) and bool(self.account)
        ready = ready and bool((self.account or {}).get('can_upload', True))
        if self.mode == 'create':
            ready = ready and bool(normalize_slug(self.slugEdit.text())
                                   if self.slugEdit is not None else '')
        else:
            ready = ready and bool(self.projectCombo.currentData()
                                   if self.projectCombo is not None else '')
        for _, check in self.consentChecks:
            ready = ready and check.isChecked()
        button = self.buttons.button(QDialogButtonBox.StandardButton.Ok)
        if button is not None:
            button.setEnabled(ready)

    @staticmethod
    def _escape(text):
        return (str(text or '').replace('&', '&amp;').replace('<', '&lt;')
                .replace('>', '&gt;'))

    # -- result ------------------------------------------------------------------

    def _dev_site_changed(self):
        """Warn as soon as the address stops being the official one."""
        self._update_api_label()
        if self._address_locked():
            return
        if is_default_site(self.siteEdit.text()):
            self.statusLabel.setText('')
        else:
            self.statusLabel.setStyleSheet('color:#b3261e;')
            self.statusLabel.setText(self.tr(
                'Development site: the project will be published on {}, not on the '
                'official site.'.format(self.siteEdit.text().strip())))

    def _address_locked(self):
        """True when the address may not be chosen by the user."""
        return self.devSiteCheck is None or not self.devSiteCheck.isChecked()

    def accept(self):
        if self._address_locked():
            # Defensive: with the address locked, nothing typed elsewhere can move the
            # upload away from the official site.
            self.siteEdit.setText(DEFAULT_SITE_URL)
        self.site_url = normalize_site_url(
            self.siteEdit.text().strip() or DEFAULT_SITE_URL)
        self.username = self.userEdit.text().strip()
        self.password = self.passwordEdit.text()
        self.remember = self.rememberCheck.isChecked() and self.rememberCheck.isEnabled()
        self.consents = [key for key, check in self.consentChecks if check.isChecked()]
        if self.mode == 'create':
            self.slug = (normalize_slug(self.slugEdit.text())
                        if self.slugEdit is not None else self.slug)
            self.display_name = (self.displayEdit.text().strip()
                                 if self.displayEdit is not None else '')
            self.target_slug = ''
        else:
            self.target_slug = (self.projectCombo.currentData()
                                if self.projectCombo is not None else '') or ''
            self.slug = self.target_slug
            selected = next((project for project in self.projects
                             if project.get('slug') == self.target_slug), {})
            self.display_name = selected.get('display_name', '')
            selected_project_id = str(selected.get('project_id') or '')
            if not self.linked_project_id or selected_project_id != self.linked_project_id:
                message = self.tr(
                    'You selected "{name}" ({slug}). It does not match the remote project identity saved with this QGIS project. Continuing will link future updates to the selected project.\n\nContinue?'
                ).format(name=self.display_name or self.target_slug,
                         slug=self.target_slug)
                if not self.linked_project_id:
                    message = self.tr(
                        'This QGIS project has no saved remote identity. The first update will link it to "{name}" ({slug}).\n\nContinue?'
                    ).format(name=self.display_name or self.target_slug,
                             slug=self.target_slug)
                answer = QMessageBox.question(
                    self, self.tr('Confirm remote project'), message,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No)
                if answer != QMessageBox.StandardButton.Yes:
                    return
            self.target_project_id = selected_project_id
        if not self.username or not self.password:
            QMessageBox.warning(
                self, self.windowTitle(),
                self.tr('The site user name and its password (or application password) '
                        'are required to publish.'))
            return
        super(CloudPublishDialog, self).accept()

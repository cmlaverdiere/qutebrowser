# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2014-2016 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.


"""Test Progress widget."""

from collections import namedtuple

import pytest

from qutebrowser.browser import webview
from qutebrowser.mainwindow.statusbar.progress import Progress


@pytest.fixture
def progress_widget(qtbot, monkeypatch, config_stub):
    """Create a Progress widget and checks its initial state."""
    config_stub.data = {
        'colors': {'statusbar.progress.bg': 'black'},
        'fonts': {},
    }
    monkeypatch.setattr(
        'qutebrowser.mainwindow.statusbar.progress.style.config', config_stub)
    widget = Progress()
    qtbot.add_widget(widget)
    assert not widget.isVisible()
    assert not widget.isTextVisible()
    return widget


def test_load_started(progress_widget):
    """Ensure the Progress widget reacts properly when the page starts loading.

    Args:
        progress_widget: Progress widget that will be tested.
    """
    progress_widget.on_load_started()
    assert progress_widget.value() == 0
    assert progress_widget.isVisible()


# mock tab object
Tab = namedtuple('Tab', 'progress load_status')


@pytest.mark.parametrize('tab, expected_visible', [
    (Tab(15, webview.LoadStatus.loading), True),
    (Tab(100, webview.LoadStatus.success), False),
    (Tab(100, webview.LoadStatus.error), False),
    (Tab(100, webview.LoadStatus.warn), False),
    (Tab(100, webview.LoadStatus.none), False),
])
def test_tab_changed(progress_widget, tab, expected_visible):
    """Test that progress widget value and visibility state match expectations.

    This uses a dummy Tab object.

    Args:
        progress_widget: Progress widget that will be tested.
    """
    progress_widget.on_tab_changed(tab)
    actual = progress_widget.value(), progress_widget.isVisible()
    expected = tab.progress, expected_visible
    assert actual == expected


def test_progress_affecting_statusbar_height(fake_statusbar, progress_widget):
    """Make sure the statusbar stays the same height when progress is shown.

    https://github.com/The-Compiler/qutebrowser/issues/886
    https://github.com/The-Compiler/qutebrowser/pull/890
    """
    expected_height = fake_statusbar.fontMetrics().height()
    assert fake_statusbar.height() == expected_height

    fake_statusbar.hbox.addWidget(progress_widget)
    progress_widget.show()

    assert fake_statusbar.height() == expected_height


def test_progress_big_statusbar(qtbot, fake_statusbar, progress_widget):
    """Make sure the progress bar is small with a big statusbar.

    https://github.com/The-Compiler/qutebrowser/commit/46d1760798b730852e2207e2cdc05a9308e44f80
    """
    fake_statusbar.hbox.addWidget(progress_widget)
    progress_widget.show()
    expected_height = progress_widget.height()
    fake_statusbar.hbox.addStrut(50)
    assert progress_widget.height() == expected_height

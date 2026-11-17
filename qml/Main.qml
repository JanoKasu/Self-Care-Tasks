
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "." as AppTheme

import "pages"

ApplicationWindow {
    id: window

    visible: true
    width: 800
    height: 480
    minimumWidth: 520
    minimumHeight: 420

    title: "Self Care Dashboard"
    color: AppTheme.Theme.canvas

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Navigation bar
        TabBar {
            id: navigation
            objectName: "navigation"

            Layout.fillWidth: true
            Layout.preferredHeight: 72
            leftPadding: 16
            rightPadding: 16
            topPadding: 10
            bottomPadding: 10
            spacing: 6

            background: Rectangle {
                color: AppTheme.Theme.surface

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 1
                    color: AppTheme.Theme.divider
                }
            }

            TabButton {
                id: homeTab
                text: "Home"
                font.pixelSize: AppTheme.Theme.fontBody
                font.weight: checked ? Font.DemiBold : Font.Normal

                background: Rectangle {
                    anchors.fill: parent
                    radius: 14
                    color: homeTab.checked ? AppTheme.Theme.accent : "transparent"
                    border.width: homeTab.checked ? 0 : 1
                    border.color: "transparent"

                    Behavior on color { ColorAnimation { duration: 180 } }
                    Behavior on border.color { ColorAnimation { duration: 180 } }
                }

                contentItem: Text {
                    text: homeTab.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    color: homeTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                    font: homeTab.font
                }
            }

            TabButton {
                id: dashboardTab
                text: "Dashboard"
                font.pixelSize: AppTheme.Theme.fontBody
                font.weight: checked ? Font.DemiBold : Font.Normal

                background: Rectangle {
                    anchors.fill: parent
                    radius: 14
                    color: dashboardTab.checked ? AppTheme.Theme.accent : "transparent"

                    Behavior on color { ColorAnimation { duration: 180 } }
                }

                contentItem: Text {
                    text: dashboardTab.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    color: dashboardTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                    font: dashboardTab.font
                }
            }

            TabButton {
                id: routinesTab
                text: "Routines"
                font.pixelSize: AppTheme.Theme.fontBody
                font.weight: checked ? Font.DemiBold : Font.Normal

                background: Rectangle {
                    anchors.fill: parent
                    radius: 14
                    color: routinesTab.checked ? AppTheme.Theme.accent : "transparent"

                    Behavior on color { ColorAnimation { duration: 180 } }
                }

                contentItem: Text {
                    text: routinesTab.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    color: routinesTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                    font: routinesTab.font
                }
            }

            TabButton {
                id: historyTab
                text: "History"
                font.pixelSize: AppTheme.Theme.fontBody
                font.weight: checked ? Font.DemiBold : Font.Normal

                background: Rectangle {
                    anchors.fill: parent
                    radius: 14
                    color: historyTab.checked ? AppTheme.Theme.accent : "transparent"

                    Behavior on color { ColorAnimation { duration: 180 } }
                }

                contentItem: Text {
                    text: historyTab.text
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    color: historyTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                    font: historyTab.font
                }
            }
        }


        // Page container
        StackLayout {
            id: pageStack
            objectName: "pageStack"

            Layout.fillWidth: true
            Layout.fillHeight: true

            currentIndex: navigation.currentIndex

            Landing {}
            Dashboard {}
            Routines {}
            History {}
        }
    }
}

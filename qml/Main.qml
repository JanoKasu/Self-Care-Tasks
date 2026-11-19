
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.VirtualKeyboard
import "." as AppTheme

import "components"
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

    RowLayout {
        anchors.fill: parent
        spacing: 0

        // Navigation bar
        Item {
            id: navigation
            objectName: "navigation"

            property int currentIndex: 0

            Layout.fillHeight: true
            Layout.preferredWidth: 88

            Rectangle {
                anchors.fill: parent
                color: AppTheme.Theme.surface

                Rectangle {
                    anchors.right: parent.right
                    width: 1
                    height: parent.height
                    color: AppTheme.Theme.divider
                }
            }

            ColumnLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.leftMargin: 12
                anchors.rightMargin: 12
                anchors.topMargin: 18
                anchors.bottomMargin: 18
                spacing: 10

                TabButton {
                    id: homeTab
                    objectName: "homeTab"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    checked: navigation.currentIndex === 0
                    hoverEnabled: true
                    Accessible.name: "Home"
                    ToolTip.text: "Home"
                    ToolTip.visible: hovered
                    onClicked: navigation.currentIndex = 0

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 14
                        color: homeTab.checked ? AppTheme.Theme.accent : "transparent"

                        Behavior on color { ColorAnimation { duration: 180 } }
                    }

                    contentItem: Column {
                        spacing: 1

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "\u2302"
                            color: homeTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                            font.pixelSize: 27
                            font.weight: Font.DemiBold
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "Home"
                            color: homeTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                        }
                    }
                }

                TabButton {
                    id: dashboardTab
                    objectName: "dashboardTab"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    checked: navigation.currentIndex === 1
                    hoverEnabled: true
                    Accessible.name: "Dashboard"
                    ToolTip.text: "Dashboard"
                    ToolTip.visible: hovered
                    onClicked: navigation.currentIndex = 1

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 14
                        color: dashboardTab.checked ? AppTheme.Theme.accent : "transparent"

                        Behavior on color { ColorAnimation { duration: 180 } }
                    }

                    contentItem: Column {
                        spacing: 1

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "\u25A6"
                            color: dashboardTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                            font.pixelSize: 23
                            font.weight: Font.DemiBold
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "Tasks"
                            color: dashboardTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                        }
                    }
                }

                TabButton {
                    id: historyTab
                    objectName: "historyTab"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    checked: navigation.currentIndex === 2
                    hoverEnabled: true
                    Accessible.name: "Progress"
                    ToolTip.text: "Progress"
                    ToolTip.visible: hovered
                    onClicked: navigation.currentIndex = 2

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 14
                        color: historyTab.checked ? AppTheme.Theme.accent : "transparent"

                        Behavior on color { ColorAnimation { duration: 180 } }
                    }

                    contentItem: Column {
                        spacing: 1

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "\u2197"
                            color: historyTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                            font.pixelSize: 26
                            font.weight: Font.DemiBold
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "Progress"
                            color: historyTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                        }
                    }
                }

                TabButton {
                    id: attentionTab
                    objectName: "attentionTab"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    checked: navigation.currentIndex === 3
                    hoverEnabled: true
                    Accessible.name: "Needs attention"
                    ToolTip.text: "Needs attention"
                    ToolTip.visible: hovered
                    onClicked: navigation.currentIndex = 3

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 14
                        color: attentionTab.checked ? AppTheme.Theme.accent : "transparent"

                        Behavior on color { ColorAnimation { duration: 180 } }
                    }

                    contentItem: Column {
                        spacing: 1

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "!"
                            color: attentionTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                            font.pixelSize: 25
                            font.weight: Font.Bold
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "Attention"
                            color: attentionTab.checked ? AppTheme.Theme.surface : AppTheme.Theme.textMuted
                            font.pixelSize: 9
                            font.weight: Font.DemiBold
                        }
                    }

                    Rectangle {
                        visible: attentionModel.count > 0
                        width: 20
                        height: 20
                        radius: 10
                        color: AppTheme.Theme.impactHigh
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.rightMargin: 5
                        anchors.topMargin: 5

                        Text {
                            anchors.centerIn: parent
                            text: Math.min(attentionModel.count, 9)
                            color: AppTheme.Theme.surface
                            font.pixelSize: 11
                            font.bold: true
                        }
                    }
                }

                Item { Layout.fillHeight: true }

                TabButton {
                    id: updateTab
                    objectName: "updateTab"
                    Layout.fillWidth: true
                    Layout.preferredHeight: 60
                    hoverEnabled: true
                    Accessible.name: "App updates"
                    ToolTip.text: "App updates"
                    ToolTip.visible: hovered
                    onClicked: updateDialog.open()

                    background: Rectangle {
                        anchors.fill: parent
                        radius: 14
                        color: updateTab.pressed ? AppTheme.Theme.canvasAlt
                                                 : "transparent"
                    }

                    contentItem: Column {
                        spacing: 1

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "\u21BB"
                            color: AppTheme.Theme.textMuted
                            font.pixelSize: 25
                            font.weight: Font.DemiBold
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            text: "Updates"
                            color: AppTheme.Theme.textMuted
                            font.pixelSize: 10
                            font.weight: Font.DemiBold
                        }
                    }

                    Rectangle {
                        visible: updateController.available
                        width: 10
                        height: 10
                        radius: 5
                        color: AppTheme.Theme.accentLight
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.rightMargin: 10
                        anchors.topMargin: 8
                    }
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

            Landing {
                onOpenTasksRequested: navigation.currentIndex = 1
            }
            Dashboard {}
            History {}
            Attention {}
        }
    }

    AppDialog {
        id: updateDialog
        objectName: "updateDialog"
        anchors.centerIn: parent
        title: "App updates"
        icon: "\u21BB"
        subtitle: "Keep the dashboard current without rebuilding it."

        ColumnLayout {
            width: parent.width
            spacing: 18

            Rectangle {
                Layout.fillWidth: true
                Layout.minimumHeight: 72
                radius: 14
                color: AppTheme.Theme.canvasAlt

                Text {
                    anchors.fill: parent
                    anchors.margins: 16
                    text: updateController.status
                    wrapMode: Text.WordWrap
                    verticalAlignment: Text.AlignVCenter
                    color: AppTheme.Theme.textSecondary
                    font.pixelSize: 14
                }
            }

            BusyIndicator {
                Layout.alignment: Qt.AlignHCenter
                visible: updateController.busy
                running: visible
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                ActionButton {
                    text: "Close"
                    Layout.fillWidth: true
                    onClicked: updateDialog.close()
                }

                ActionButton {
                    text: updateController.available ? "Update" : "Check"
                    Layout.fillWidth: true
                    primary: true
                    enabled: !updateController.busy
                    onClicked: updateController.available
                               ? updateController.applyUpdate()
                               : updateController.checkForUpdates()
                }

                ActionButton {
                    text: "Restart"
                    Layout.fillWidth: true
                    enabled: !updateController.busy
                             && updateController.status.startsWith("Update complete")
                    visible: updateController.status.startsWith("Update complete")
                    primary: true
                    onClicked: updateController.restart()
                }
            }
        }
    }

    InputPanel {
        id: virtualKeyboard
        objectName: "virtualKeyboard"
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        z: 100
        visible: active
    }
}

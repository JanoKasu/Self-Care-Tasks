import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as AppTheme
import "../components"

Item {
    id: root
    objectName: "githubPage"

    Rectangle {
        anchors.fill: parent
        color: AppTheme.Theme.canvas
    }

    ScrollView {
        anchors.fill: parent
        contentWidth: availableWidth
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: 16

            Item { Layout.preferredHeight: 4 }
            ColumnLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 24
                Layout.rightMargin: 24
                spacing: 3
                Text {
                    text: "GitHub Contributions"
                    font.pixelSize: AppTheme.Theme.fontTitle
                    font.bold: true
                    color: AppTheme.Theme.textPrimary
                }
                Text {
                    text: githubController.login ? "@" + githubController.login : "Your coding activity"
                    font.pixelSize: 14
                    color: AppTheme.Theme.textSecondary
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 24
                Layout.rightMargin: 24
                Layout.preferredHeight: cardContent.implicitHeight + 36
                radius: AppTheme.Theme.radiusLarge
                color: AppTheme.Theme.surface
                border.width: 1
                border.color: AppTheme.Theme.divider

                ColumnLayout {
                    id: cardContent
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    anchors.margins: 18
                    spacing: 12

                    Text {
                        Layout.fillWidth: true
                        text: githubController.status
                        wrapMode: Text.WordWrap
                        color: AppTheme.Theme.textSecondary
                        font.pixelSize: 13
                    }

                    RowLayout {
                        visible: githubController.userCode !== ""
                        Layout.fillWidth: true
                        spacing: 18
                        Image {
                            objectName: "githubQr"
                            source: "image://github/qr"
                            sourceSize.width: 180
                            sourceSize.height: 180
                            Layout.preferredWidth: 150
                            Layout.preferredHeight: 150
                            smooth: false
                            fillMode: Image.PreserveAspectFit
                        }
                        ColumnLayout {
                            Layout.fillWidth: true
                            Text {
                                Layout.fillWidth: true
                                text: "1. Scan with your phone\n2. Enter this code on GitHub:"
                                wrapMode: Text.WordWrap
                                color: AppTheme.Theme.textPrimary
                                font.pixelSize: 14
                            }
                            Text {
                                text: githubController.userCode
                                color: AppTheme.Theme.accent
                                font.pixelSize: 24
                                font.bold: true
                            }
                            Text {
                                Layout.fillWidth: true
                                text: "github.com/login/device"
                                color: AppTheme.Theme.textSecondary
                                font.pixelSize: 12
                                wrapMode: Text.WordWrap
                            }
                        }
                    }

                    ColumnLayout {
                        visible: githubController.connected && githubController.weeks.length > 0
                        Layout.fillWidth: true
                        spacing: 10
                        Text {
                            text: githubController.total + " contributions in the last year"
                            color: AppTheme.Theme.textPrimary
                            font.pixelSize: 18
                            font.bold: true
                        }
                        ScrollView {
                            Layout.fillWidth: true
                            Layout.preferredHeight: 132
                            contentWidth: graph.implicitWidth
                            contentHeight: graph.implicitHeight
                            clip: true
                            ScrollBar.vertical.policy: ScrollBar.AlwaysOff
                            Row {
                                id: graph
                                spacing: 3
                                Repeater {
                                    model: githubController.weeks
                                    delegate: Column {
                                        id: week
                                        required property var modelData
                                        spacing: 3
                                        Repeater {
                                            model: 7
                                            delegate: Rectangle {
                                                objectName: "contributionDay"
                                                required property int index
                                                property var day: {
                                                    var days = week.modelData.contributionDays
                                                    for (var i = 0; i < days.length; i++) {
                                                        if (days[i].weekday === index)
                                                            return days[i]
                                                    }
                                                    return null
                                                }
                                                width: 12
                                                height: 12
                                                radius: 3
                                                color: !day || day.contributionLevel === "NONE"
                                                       ? AppTheme.Theme.progressTrack
                                                       : day.contributionLevel === "FIRST_QUARTILE" ? "#9be9a8"
                                                       : day.contributionLevel === "SECOND_QUARTILE" ? "#40c463"
                                                       : day.contributionLevel === "THIRD_QUARTILE" ? "#30a14e"
                                                       : "#216e39"
                                                opacity: day ? 1 : 0
                                                ToolTip.visible: mouse.containsMouse && day !== null
                                                ToolTip.text: day ? day.date + ": " + day.contributionCount + " contributions" : ""
                                                MouseArea {
                                                    id: mouse
                                                    anchors.fill: parent
                                                    hoverEnabled: true
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        ActionButton {
                            visible: !githubController.connected && githubController.userCode === ""
                            enabled: !githubController.busy
                            text: "Connect GitHub"
                            primary: true
                            onClicked: githubController.connectGitHub()
                        }
                        ActionButton {
                            visible: githubController.connected
                            enabled: !githubController.busy
                            text: "Refresh"
                            primary: true
                            onClicked: githubController.refresh()
                        }
                        ActionButton {
                            visible: githubController.connected || githubController.busy
                            text: githubController.connected ? "Disconnect" : "Cancel"
                            onClicked: githubController.disconnectGitHub()
                        }
                        Item { Layout.fillWidth: true }
                    }
                }
            }
            Item { Layout.preferredHeight: 4 }
        }
    }
}

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as AppTheme

Item {
    id: root
    objectName: "settingsPage"

    Component.onCompleted: networkController.scanNetworks()

    Rectangle {
        anchors.fill: parent
        color: AppTheme.Theme.canvas
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 18

        ColumnLayout {
            spacing: 3

            Text {
                text: "Settings"
                font.pixelSize: AppTheme.Theme.fontTitle
                font.bold: true
                color: AppTheme.Theme.textPrimary
            }

            Text {
                text: "Manage your internet connection"
                font.pixelSize: 14
                color: AppTheme.Theme.textSecondary
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.maximumWidth: 620
            Layout.preferredHeight: 330
            radius: AppTheme.Theme.radiusLarge
            color: AppTheme.Theme.surface
            border.width: 1
            border.color: AppTheme.Theme.divider

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 14

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Rectangle {
                        Layout.preferredWidth: 12
                        Layout.preferredHeight: 12
                        radius: 6
                        color: networkController.connected
                               ? AppTheme.Theme.impactMedium
                               : AppTheme.Theme.impactHigh
                    }

                    Text {
                        text: networkController.connected
                              ? "Internet connected"
                              : "Internet disconnected"
                        font.pixelSize: 17
                        font.bold: true
                        color: AppTheme.Theme.textPrimary
                    }

                    Item { Layout.fillWidth: true }

                    Button {
                        text: "Rescan"
                        enabled: !networkController.checking
                        onClicked: networkController.scanNetworks()
                    }
                }

                ComboBox {
                    id: wifiNetwork
                    Layout.fillWidth: true
                    Layout.preferredHeight: 54
                    editable: true
                    currentIndex: -1
                    model: networkController.networks

                    font.pixelSize: 16
                    leftPadding: 16
                    rightPadding: 16

                    background: Rectangle {
                        radius: 14
                        color: AppTheme.Theme.canvas
                        border.width: 1
                        border.color: wifiNetwork.activeFocus
                                      ? AppTheme.Theme.accent
                                      : AppTheme.Theme.divider
                    }

                    contentItem: TextInput {
                        text: wifiNetwork.editText
                        font.pixelSize: 16
                        color: AppTheme.Theme.textPrimary
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 16
                        rightPadding: 16
                        selectByMouse: true
                        readOnly: !wifiNetwork.editable
                        onTextChanged: wifiNetwork.editText = text
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    TextField {
                        id: wifiPassword
                        Layout.fillWidth: true
                        Layout.preferredHeight: 54
                        placeholderText: "Wi-Fi password"
                        echoMode: passwordVisible.isPasswordVisible
                                  ? TextInput.Normal
                                  : TextInput.Password
                        font.pixelSize: 16
                        leftPadding: 16
                        rightPadding: 16

                        background: Rectangle {
                            radius: 14
                            color: AppTheme.Theme.canvas
                            border.width: 1
                            border.color: wifiPassword.activeFocus
                                          ? AppTheme.Theme.accent
                                          : AppTheme.Theme.divider
                        }
                    }

                    Button {
                        id: passwordVisible
                        property bool isPasswordVisible: false
                        Layout.preferredWidth: 112
                        Layout.preferredHeight: 54
                        text: isPasswordVisible ? "Hide" : "Show"

                        background: Rectangle {
                            radius: 14
                            color: passwordVisible.isPasswordVisible
                                   ? AppTheme.Theme.accentLight
                                   : AppTheme.Theme.canvas
                            border.width: 1
                            border.color: AppTheme.Theme.divider
                        }

                        contentItem: Text {
                            text: passwordVisible.text
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 15
                            font.bold: true
                            color: passwordVisible.isPasswordVisible
                                   ? AppTheme.Theme.surface
                                   : AppTheme.Theme.textPrimary
                        }

                        onClicked: isPasswordVisible = !isPasswordVisible
                    }
                }

                Text {
                    Layout.fillWidth: true
                    text: networkController.status
                    wrapMode: Text.WordWrap
                    color: AppTheme.Theme.textSecondary
                    font.pixelSize: 13
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Item { Layout.fillWidth: true }

                    Button {
                        text: "Check connection"
                        onClicked: networkController.checkConnection()
                    }

                    Button {
                        text: "Connect"
                        enabled: !networkController.checking
                                 && wifiNetwork.editText.length > 0
                        onClicked: networkController.connectNetwork(
                            wifiNetwork.editText,
                            wifiPassword.text
                        )
                    }
                }
            }
        }

        Item { Layout.fillHeight: true }
    }
}

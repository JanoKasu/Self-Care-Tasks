import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as AppTheme

Item {
    id: root

    Rectangle {
        anchors.fill: parent
        color: AppTheme.Theme.canvas
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 24
        spacing: 18

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                spacing: 3

                Text {
                    text: "Completion History"
                    font.pixelSize: AppTheme.Theme.fontTitle
                    font.bold: true
                    color: AppTheme.Theme.textPrimary
                }

                Text {
                    text: "Task completions from the past 30 days"
                    font.pixelSize: 14
                    color: AppTheme.Theme.textSecondary
                }
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                Layout.preferredWidth: 112
                Layout.preferredHeight: 38
                radius: 19
                color: AppTheme.Theme.accentLight

                Text {
                    anchors.centerIn: parent
                    text: historyModel.count + (historyModel.count === 1 ? " task" : " tasks")
                    color: AppTheme.Theme.surface
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                }
            }
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            ColumnLayout {
                width: parent.width
                spacing: 12

                Repeater {
                    model: historyModel

                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 96
                        radius: AppTheme.Theme.radiusLarge
                        color: AppTheme.Theme.surface
                        border.width: 1
                        border.color: AppTheme.Theme.divider

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 14

                            Rectangle {
                                Layout.preferredWidth: 58
                                Layout.preferredHeight: 58
                                radius: 18
                                color: model.backgroundColor

                                Text {
                                    anchors.centerIn: parent
                                    text: model.taskIcon
                                    font.pixelSize: 24
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 5

                                Text {
                                    Layout.fillWidth: true
                                    text: model.title
                                    font.pixelSize: 16
                                    font.bold: true
                                    color: AppTheme.Theme.textPrimary
                                    elide: Text.ElideRight
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: model.description
                                    font.pixelSize: 12
                                    color: AppTheme.Theme.textSecondary
                                    elide: Text.ElideRight
                                }
                            }

                            ColumnLayout {
                                Layout.preferredWidth: 150
                                spacing: 4

                                Text {
                                    Layout.alignment: Qt.AlignRight
                                    text: model.completionCount + (model.completionCount === 1 ? " time" : " times")
                                    font.pixelSize: 11
                                    font.bold: true
                                    color: AppTheme.Theme.accent
                                }
                            }
                        }
                    }
                }

                Item {
                    visible: historyModel.count === 0
                    Layout.fillWidth: true
                    Layout.preferredHeight: 220

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 10

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "✓"
                            font.pixelSize: 42
                            color: AppTheme.Theme.accentLight
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "No completions yet"
                            font.pixelSize: 18
                            font.bold: true
                            color: AppTheme.Theme.textPrimary
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Completed tasks will appear here"
                            font.pixelSize: 13
                            color: AppTheme.Theme.textSecondary
                        }
                    }
                }
            }
        }
    }
}

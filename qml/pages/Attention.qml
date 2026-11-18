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
                    text: "Needs Attention"
                    font.pixelSize: AppTheme.Theme.fontTitle
                    font.bold: true
                    color: AppTheme.Theme.textPrimary
                }

                Text {
                    text: "Scheduled tasks with missed occurrences"
                    font.pixelSize: 14
                    color: AppTheme.Theme.textSecondary
                }
            }

            Item { Layout.fillWidth: true }

            Rectangle {
                Layout.preferredWidth: 126
                Layout.preferredHeight: 38
                radius: 19
                color: attentionModel.count > 0
                       ? AppTheme.Theme.impactHighSurface
                       : AppTheme.Theme.taskMint

                Text {
                    anchors.centerIn: parent
                    text: attentionModel.count
                          + (attentionModel.count === 1 ? " task" : " tasks")
                    color: attentionModel.count > 0
                           ? AppTheme.Theme.impactHigh
                           : AppTheme.Theme.impactMedium
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
                    model: attentionModel

                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 104
                        radius: AppTheme.Theme.radiusLarge
                        color: AppTheme.Theme.surface
                        border.width: 1
                        border.color: AppTheme.Theme.divider

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 14

                            Rectangle {
                                Layout.preferredWidth: 62
                                Layout.preferredHeight: 62
                                radius: 18
                                color: model.backgroundColor

                                Text {
                                    anchors.centerIn: parent
                                    text: model.taskIcon
                                    font.pixelSize: 27
                                }
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 5

                                Text {
                                    Layout.fillWidth: true
                                    text: model.title
                                    color: AppTheme.Theme.textPrimary
                                    font.pixelSize: 17
                                    font.bold: true
                                    elide: Text.ElideRight
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: model.frequency + " • " + model.impact + " priority"
                                    color: AppTheme.Theme.textSecondary
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                            }

                            ColumnLayout {
                                Layout.preferredWidth: 124
                                spacing: 5

                                Text {
                                    Layout.alignment: Qt.AlignRight
                                    text: model.missed
                                          + (model.missed === 1 ? " missed" : " missed")
                                    color: AppTheme.Theme.impactHigh
                                    font.pixelSize: 13
                                    font.bold: true
                                }

                                Text {
                                    Layout.alignment: Qt.AlignRight
                                    text: model.completionRate + "% completed"
                                    color: AppTheme.Theme.textSecondary
                                    font.pixelSize: 11
                                }
                            }
                        }
                    }
                }

                Item {
                    visible: attentionModel.count === 0
                    Layout.fillWidth: true
                    Layout.preferredHeight: 240

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 9

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "✓"
                            color: AppTheme.Theme.impactMedium
                            font.pixelSize: 44
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Nothing needs attention"
                            color: AppTheme.Theme.textPrimary
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "Keep up the steady progress"
                            color: AppTheme.Theme.textSecondary
                            font.pixelSize: 13
                        }
                    }
                }
            }
        }
    }
}

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

    ScrollView {
        id: historyScroll
        anchors.fill: parent
        anchors.margins: root.width < 560 ? 16 : 24
        clip: true
        ScrollBar.vertical.policy: ScrollBar.AsNeeded
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

        ColumnLayout {
            width: historyScroll.availableWidth
            spacing: 18

        ColumnLayout {
            spacing: 3

            Text {
                text: "Your Progress"
                font.pixelSize: AppTheme.Theme.fontTitle
                font.bold: true
                color: AppTheme.Theme.textPrimary
            }

            Text {
                text: "Every small step adds up"
                font.pixelSize: 14
                color: AppTheme.Theme.textSecondary
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 148
            radius: AppTheme.Theme.radiusLarge
            color: AppTheme.Theme.surface
            border.width: 1
            border.color: AppTheme.Theme.divider

            RowLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 24

                Rectangle {
                    Layout.preferredWidth: 104
                    Layout.preferredHeight: 104
                    radius: 52
                    color: AppTheme.Theme.accent

                    ColumnLayout {
                        anchors.centerIn: parent
                        spacing: 1

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: "LEVEL"
                            color: AppTheme.Theme.surface
                            opacity: 0.75
                            font.pixelSize: 11
                            font.letterSpacing: 1.5
                            font.weight: Font.DemiBold
                        }

                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            text: taskModel.level
                            color: AppTheme.Theme.surface
                            font.pixelSize: 38
                            font.bold: true
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    RowLayout {
                        Layout.fillWidth: true

                        Text {
                            text: taskModel.xp + " total XP"
                            color: AppTheme.Theme.textPrimary
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Item { Layout.fillWidth: true }

                        Text {
                            text: taskModel.pointsToNextLevel + " XP to level "
                                  + (taskModel.level + 1)
                            color: AppTheme.Theme.textSecondary
                            font.pixelSize: 12
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        height: 12
                        radius: 6
                        color: AppTheme.Theme.progressTrack

                        Rectangle {
                            width: parent.width * taskModel.levelProgress / 100
                            height: parent.height
                            radius: parent.radius
                            color: AppTheme.Theme.accentLight

                            Behavior on width {
                                NumberAnimation { duration: 220 }
                            }
                        }
                    }

                    Text {
                        text: taskModel.levelProgress + "% of the way to your next level"
                        color: AppTheme.Theme.textSecondary
                        font.pixelSize: 12
                    }
                }
            }
        }

        GridLayout {
            id: statsGrid
            objectName: "statsGrid"
            Layout.fillWidth: true
            Layout.preferredHeight: root.width < 560 ? 300 : 220
            Layout.minimumHeight: 220
            columns: 2
            rowSpacing: 14
            columnSpacing: 14

            Repeater {
                model: [
                    {
                        "icon": "✓",
                        "value": taskModel.totalCompletions,
                        "label": "Completions in 30 days"
                    },
                    {
                        "icon": "↗",
                        "value": taskModel.completionRate + "%",
                        "label": "Schedule completion"
                    },
                    {
                        "icon": "☀",
                        "value": taskModel.currentStreak,
                        "label": "Current daily streak"
                    },
                    {
                        "icon": "★",
                        "value": taskModel.bestStreak,
                        "label": "Best daily streak"
                    }
                ]

                delegate: Rectangle {
                    required property var modelData

                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: AppTheme.Theme.radiusMedium
                    color: AppTheme.Theme.surface
                    border.width: 1
                    border.color: AppTheme.Theme.divider

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 14

                        Rectangle {
                            Layout.preferredWidth: 50
                            Layout.preferredHeight: 50
                            radius: 16
                            color: AppTheme.Theme.canvasAlt

                            Text {
                                anchors.centerIn: parent
                                text: modelData.icon
                                color: AppTheme.Theme.accent
                                font.pixelSize: 24
                                font.bold: true
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 0
                            spacing: 3

                            Text {
                                text: modelData.value
                                color: AppTheme.Theme.textPrimary
                                font.pixelSize: 25
                                font.bold: true
                            }

                            Text {
                                Layout.fillWidth: true
                                maximumLineCount: 2
                                elide: Text.ElideRight
                                text: modelData.label
                                color: AppTheme.Theme.textSecondary
                                font.pixelSize: 12
                                wrapMode: Text.WordWrap
                            }
                        }
                        }
                    }
                }
            }
        }
    }
}

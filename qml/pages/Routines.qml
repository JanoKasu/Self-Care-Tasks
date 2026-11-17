
import QtQuick
import QtQuick.Layouts
import ".." as AppTheme

Item {
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
                text: "Your Routines"
                font.pixelSize: AppTheme.Theme.fontTitle
                font.bold: true
                color: AppTheme.Theme.textPrimary
            }
            Text {
                text: "Create a rhythm that feels good"
                font.pixelSize: 14
                color: AppTheme.Theme.textSecondary
            }
        }

        GridLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            columns: parent.width < 700 ? 1 : 2
            rowSpacing: 14
            columnSpacing: 14

            Repeater {
                model: [
                    {name: "Morning Reset", icon: "☀", detail: "Start gently", color: AppTheme.Theme.morning},
                    {name: "Midday Pause", icon: "◌", detail: "Breathe and reset", color: AppTheme.Theme.midday},
                    {name: "Evening Wind Down", icon: "☾", detail: "Prepare for rest", color: AppTheme.Theme.evening},
                    {name: "Weekly Reflection", icon: "✦", detail: "Notice your progress", color: AppTheme.Theme.reflection}
                ]

                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 150
                    radius: 22
                    color: modelData.color

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 18
                        spacing: 8

                        Rectangle {
                            Layout.preferredWidth: 44
                            Layout.preferredHeight: 44
                            radius: 14
                            color: AppTheme.Theme.surface
                            opacity: 0.82

                            Text {
                                anchors.centerIn: parent
                                text: modelData.icon
                                font.pixelSize: 22
                                color: AppTheme.Theme.textPrimary
                            }
                        }

                        Text {
                            text: modelData.name
                            font.pixelSize: 18
                            font.bold: true
                            color: AppTheme.Theme.textPrimary
                        }

                        Text {
                            text: modelData.detail
                            font.pixelSize: 13
                            color: AppTheme.Theme.textSecondary
                        }
                    }
                }
            }
        }
    }
}

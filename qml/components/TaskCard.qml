
import QtQuick
import QtQuick.Layouts
import "."
import ".." as AppTheme

Rectangle {
    id: root

    // Task data
    property string title: "Drink Water"
    property string description: "Stay hydrated throughout the day."
    property string taskIcon: "💧"

    // Appearance
    property color backgroundColor: AppTheme.Theme.taskPeach
    property color accentColor: AppTheme.Theme.accentPeach

    // Task metadata
    property string createdAt: ""
    property string durationOnBoard: "0m"
    property string impact: "High"
    property date boardTime: new Date()

    // Completion state
    property bool completed: false

    signal completionRequested(bool completed)

    implicitWidth: 350
    implicitHeight: 156

    radius: AppTheme.Theme.radiusLarge
    color: root.backgroundColor
    layer.enabled: true

    border.width: 1
    border.color: Qt.darker(backgroundColor, 1.08)

    function refreshDuration() {
        if (!createdAt)
            return

        var created = new Date(createdAt)
        if (isNaN(created.getTime()))
            return

        var elapsedMinutes = Math.floor(
            Math.max(0, boardTime.getTime() - created.getTime()) / 60000
        )
        if (elapsedMinutes < 60) {
            durationOnBoard = elapsedMinutes + "m"
            return
        }

        var hours = Math.floor(elapsedMinutes / 60)
        var minutes = elapsedMinutes % 60
        durationOnBoard = hours + "h " + minutes + "m"
    }

    onCreatedAtChanged: refreshDuration()

    Timer {
        interval: 60000
        running: true
        repeat: true
        onTriggered: {
            boardTime = new Date()
            root.refreshDuration()
        }
    }

    Behavior on color {
        ColorAnimation { duration: 180 }
    }

    RowLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 14

        // Task icon
        Rectangle {
            Layout.preferredWidth: 58
            Layout.preferredHeight: 58
            radius: 18
            color: AppTheme.Theme.surface
            opacity: 0.8

            Text {
                anchors.centerIn: parent
                text: root.taskIcon
                font.pixelSize: 28
            }
        }

        // Task information
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 7

            Text {
                Layout.fillWidth: true
                text: root.title
                color: AppTheme.Theme.textPrimary
                font.pixelSize: 18
                font.weight: Font.Bold
                elide: Text.ElideRight
            }

            Text {
                Layout.fillWidth: true
                text: root.description
                color: AppTheme.Theme.textSecondary
                font.pixelSize: 13
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }

            RowLayout {
                spacing: 6

                InfoPill {
                    icon: "◷"
                    text: root.durationOnBoard
                    accentColor: AppTheme.Theme.accent
                    backgroundColor: AppTheme.Theme.surface
                }

                InfoPill {
                    text: root.impact + " impact"
                    accentColor: root.impact === "High"
                                ? AppTheme.Theme.impactHigh
                                : root.impact === "Medium"
                                  ? AppTheme.Theme.impactMedium
                                  : AppTheme.Theme.impactLow

                    backgroundColor: root.impact === "High"
                                     ? AppTheme.Theme.impactHighSurface
                                     : root.impact === "Medium"
                                       ? AppTheme.Theme.taskMint
                                       : AppTheme.Theme.impactLowSurface
                }
            }
        }

        Checkbox {
            checked: root.completed

            boxSize: 38
            cornerRadius: 10

            checkedColor: AppTheme.Theme.accentLight
            uncheckedColor: AppTheme.Theme.surface
            borderColor: AppTheme.Theme.checkboxBorder
            checkColor: AppTheme.Theme.surface

            onToggled: function(isChecked) {
                root.completed = isChecked
                root.completionRequested(isChecked)
            }
        }
    }
}


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
    property string durationStartedAt: createdAt
    property string durationOnBoard: "0m"
    property string impact: "High"
    property string frequency: "Daily"
    property int points: 10
    property date boardTime: new Date()

    // Completion state
    property bool completed: false

    signal completionRequested(bool completed)
    signal deleteRequested()

    implicitWidth: 350
    implicitHeight: 156

    radius: AppTheme.Theme.radiusLarge
    gradient: Gradient {
        GradientStop {
            position: 0
            color: root.impact === "High"
                   ? AppTheme.Theme.impactHighGradientStart
                   : root.impact === "Medium"
                     ? AppTheme.Theme.impactMediumGradientStart
                     : AppTheme.Theme.impactLowGradientStart
        }
        GradientStop {
            position: 1
            color: root.impact === "High"
                   ? AppTheme.Theme.impactHighGradientEnd
                   : root.impact === "Medium"
                     ? AppTheme.Theme.impactMediumGradientEnd
                     : AppTheme.Theme.impactLowGradientEnd
        }
    }
    layer.enabled: true
    opacity: root.completed ? 0.82 : 1

    border.width: 1
    border.color: root.impact === "High"
                  ? AppTheme.Theme.impactHigh
                  : root.impact === "Medium"
                    ? AppTheme.Theme.impactMedium
                    : AppTheme.Theme.impactLow

    function refreshDuration() {
        if (!durationStartedAt)
            return

        var created = new Date(durationStartedAt)
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

    onDurationStartedAtChanged: refreshDuration()

    Timer {
        interval: 60000
        running: true
        repeat: true
        onTriggered: {
            boardTime = new Date()
            root.refreshDuration()
        }
    }

    Behavior on opacity {
        NumberAnimation { duration: 180 }
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
                color: root.completed
                       ? AppTheme.Theme.textMuted
                       : AppTheme.Theme.textPrimary
                font.pixelSize: 18
                font.weight: Font.Bold
                font.strikeout: root.completed
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

            Flow {
                Layout.fillWidth: true
                spacing: 6

                InfoPill {
                    objectName: "durationPill"
                    visible: !root.completed
                    icon: "◷"
                    text: root.durationOnBoard
                    accentColor: AppTheme.Theme.accent
                    backgroundColor: AppTheme.Theme.surface
                }

                InfoPill {
                    text: root.impact + " priority"
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

                InfoPill {
                    text: root.frequency
                    accentColor: AppTheme.Theme.accent
                    backgroundColor: AppTheme.Theme.surface
                }

                InfoPill {
                    text: "+" + root.points + " XP"
                    accentColor: AppTheme.Theme.accent
                    backgroundColor: AppTheme.Theme.surface
                }
            }
        }

        Checkbox {
            checked: root.completed
            accessibleName: root.completed
                            ? "Mark " + root.title + " incomplete"
                            : "Mark " + root.title + " complete"

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

            onLongPressed: root.deleteRequested()
        }
    }
}

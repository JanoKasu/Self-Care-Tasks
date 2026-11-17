
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "."

Rectangle {
    id: root

    // Task data
    property string title: "Drink Water"
    property string description: "Stay hydrated throughout the day."
    property string taskIcon: "💧"

    // Appearance
    property color backgroundColor: "#FBE3D5"
    property color accentColor: "#C47C58"

    // Task metadata
    property string durationOnBoard: "2h 15m"
    property string impact: "High"

    // Completion state
    property bool completed: false

    signal completionRequested(bool completed)

    implicitWidth: 350
    implicitHeight: 145

    radius: 20
    color: root.backgroundColor

    border.width: 1
    border.color: Qt.darker(backgroundColor, 1.08)

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
            color: "#FFFFFF"
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
                color: "#493D5C"
                font.pixelSize: 17
                font.weight: Font.Bold
                elide: Text.ElideRight
            }

            Text {
                Layout.fillWidth: true
                text: root.description
                color: "#756A83"
                font.pixelSize: 11
                wrapMode: Text.WordWrap
                maximumLineCount: 2
                elide: Text.ElideRight
            }

            RowLayout {
                spacing: 6

                InfoPill {
                    icon: "◷"
                    text: root.durationOnBoard
                    accentColor: "#75618F"
                    backgroundColor: "#FFFFFF"
                }

                InfoPill {
                    text: root.impact + " impact"
                    accentColor: root.impact === "High"
                                ? "#B84E65"
                                : root.impact === "Medium"
                                  ? "#477A60"
                                  : "#92743A"

                    backgroundColor: root.impact === "High"
                                     ? "#F9DCE3"
                                     : root.impact === "Medium"
                                       ? "#DCEFE5"
                                       : "#F9EDC9"
                }
            }
        }

        Checkbox {
            checked: true

            boxSize: 32
            cornerRadius: 10

            checkedColor: "#A98BD4"
            uncheckedColor: "#FFFFFF"
            borderColor: "#B7A9C7"
            checkColor: "#FFFFFF"
        }
    }
}

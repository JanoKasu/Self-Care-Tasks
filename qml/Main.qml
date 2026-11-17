
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "pages"

ApplicationWindow {
    id: window

    visible: true
    width: 800
    height: 480
    minimumWidth: 520
    minimumHeight: 420

    title: "Self Care Dashboard"
    color: "#F5F0FA"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Navigation bar
        TabBar {
            id: navigation

            Layout.fillWidth: true
            Layout.preferredHeight: 54

            background: Rectangle {
                color: "#FFFFFF"

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: parent.width
                    height: 3
                    color: "#E7E1EB"
                }

                Rectangle {
                    anchors.bottom: parent.bottom
                    width: navigation.width / 4
                    height: 3
                    x: navigation.currentIndex * width
                    color: "#A98BD4"

                    Behavior on x {
                        NumberAnimation {
                            duration: 180
                            easing.type: Easing.OutCubic
                        }
                    }
                }
            }

            TabButton {
                text: "Dashboard"
            }

            TabButton {
                text: "Routines"
            }
        }


        // Page container
        StackLayout {
            id: pageStack

            Layout.fillWidth: true
            Layout.fillHeight: true

            currentIndex: navigation.currentIndex

            Dashboard {}
            Routines {}
        }
    }
}

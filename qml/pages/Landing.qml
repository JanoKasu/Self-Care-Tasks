import QtQuick
import QtQuick.Layouts
import ".." as AppTheme

Item {
    id: root

    property date now: new Date()

    Rectangle {
        anchors.fill: parent

        gradient: Gradient {
            GradientStop {
                position: 0
                color: AppTheme.Theme.landingStart
            }
            GradientStop {
                position: 0.48
                color: AppTheme.Theme.landingMiddle
            }
            GradientStop {
                position: 1
                color: AppTheme.Theme.landingEnd
            }
        }

        Rectangle {
            width: 230
            height: 230
            radius: 115
            x: parent.width - width - 40
            y: -70
            color: AppTheme.Theme.landingGold
            opacity: 0.28
        }

        Rectangle {
            width: 170
            height: 170
            radius: 85
            x: -50
            y: parent.height - 70
            color: AppTheme.Theme.landingMint
            opacity: 0.25
        }

        Rectangle {
            anchors.fill: parent
            anchors.margins: 18
            radius: 30
            color: AppTheme.Theme.surface
            opacity: 0.10
            border.width: 1
            border.color: AppTheme.Theme.surface
        }

        ColumnLayout {
            anchors.centerIn: parent
            width: Math.min(parent.width - 48, 620)
            spacing: 8

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Take a moment for yourself"
                font.pixelSize: 15
                font.weight: Font.DemiBold
                font.letterSpacing: 1
                color: AppTheme.Theme.landingWhite
                opacity: 0.92
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: Qt.formatTime(root.now, "h:mm")
                font.pixelSize: Math.min(92, root.width * 0.14)
                font.weight: Font.ExtraLight
                font.letterSpacing: 3
                color: AppTheme.Theme.landingWhite
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: Qt.formatTime(root.now, "AP")
                font.pixelSize: 16
                font.weight: Font.Bold
                color: AppTheme.Theme.landingCream
            }

            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                Layout.preferredWidth: 160
                Layout.preferredHeight: 2
                radius: 1
                color: AppTheme.Theme.landingWhite
                opacity: 0.55
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                Layout.topMargin: 8
                text: Qt.formatDate(root.now, "dddd")
                font.pixelSize: 22
                font.weight: Font.DemiBold
                color: AppTheme.Theme.landingWhite
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: Qt.formatDate(root.now, "MMMM d, yyyy")
                font.pixelSize: 16
                color: AppTheme.Theme.landingSoftWhite
                opacity: 0.92
            }
        }
    }

    Timer {
        interval: 1000
        running: true
        repeat: true
        triggeredOnStart: true
        onTriggered: root.now = new Date()
    }
}

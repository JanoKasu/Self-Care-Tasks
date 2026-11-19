import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "../components"
import ".." as AppTheme

Item {
    id: root

    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0; color: AppTheme.Theme.canvas }
            GradientStop { position: 1; color: AppTheme.Theme.canvasAlt }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: root.width < 560 ? 16 : 24
        spacing: 16

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                spacing: 3

                Text {
                    Layout.fillWidth: true
                    text: weatherController.hasLocation
                          ? weatherController.locationName
                          : "Weather"
                    color: AppTheme.Theme.textPrimary
                    font.pixelSize: 28
                    font.bold: true
                    elide: Text.ElideRight
                }

                Text {
                    text: weatherController.hasLocation
                          ? weatherController.status
                          : "Forecasts from Open-Meteo"
                    color: AppTheme.Theme.textSecondary
                    font.pixelSize: 13
                }
            }

            Item { Layout.fillWidth: true }

            ActionButton {
                text: weatherController.hasLocation ? "Change city" : "Choose city"
                enabled: !weatherController.busy
                onClicked: {
                    locationDialog.open()
                    citySearchField.forceActiveFocus()
                }
            }

            ActionButton {
                text: "↻"
                Layout.preferredWidth: 52
                Layout.minimumWidth: 52
                visible: weatherController.hasLocation
                enabled: !weatherController.busy
                Accessible.name: "Refresh weather"
                onClicked: weatherController.refresh()
            }
        }

        BusyIndicator {
            Layout.alignment: Qt.AlignHCenter
            visible: weatherController.busy
            running: visible
        }

        Rectangle {
            visible: !weatherController.hasLocation
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: AppTheme.Theme.radiusLarge
            color: AppTheme.Theme.surface
            border.width: 1
            border.color: AppTheme.Theme.divider

            ColumnLayout {
                anchors.centerIn: parent
                width: Math.min(parent.width - 40, 460)
                spacing: 12

                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "🌤"
                    font.pixelSize: 62
                }

                Text {
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    text: "Add your city to see today's weather"
                    color: AppTheme.Theme.textPrimary
                    font.pixelSize: 20
                    font.bold: true
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    text: "Your location is saved on this device. Weather data is not used to track task activity."
                    color: AppTheme.Theme.textSecondary
                    font.pixelSize: 13
                    wrapMode: Text.WordWrap
                }

                ActionButton {
                    Layout.alignment: Qt.AlignHCenter
                    text: "Choose a city"
                    primary: true
                    onClicked: {
                        locationDialog.open()
                        citySearchField.forceActiveFocus()
                    }
                }
            }
        }

        ScrollView {
            id: weatherScroll
            objectName: "weatherScroll"
            visible: weatherController.hasLocation
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            contentWidth: availableWidth
            ScrollBar.vertical.policy: ScrollBar.AsNeeded
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            ColumnLayout {
                width: weatherScroll.availableWidth
                spacing: 14

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: root.width < 560 ? 238 : 158
                    radius: AppTheme.Theme.radiusLarge
                    color: AppTheme.Theme.surface
                    border.width: 1
                    border.color: AppTheme.Theme.divider

                    GridLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        columns: root.width < 560 ? 2 : 3
                        rowSpacing: 10
                        columnSpacing: 16

                        Text {
                            text: weatherController.current.icon || "🌡"
                            font.pixelSize: 54
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 1

                            Text {
                                text: (weatherController.current.temperature || 0) + "°"
                                color: AppTheme.Theme.textPrimary
                                font.pixelSize: 48
                                font.bold: true
                            }

                            Text {
                                text: weatherController.current.description || "Loading..."
                                color: AppTheme.Theme.textPrimary
                                font.pixelSize: 16
                                font.weight: Font.DemiBold
                                wrapMode: Text.WordWrap
                            }

                            Text {
                                text: "Feels like "
                                      + (weatherController.current.feelsLike || 0)
                                      + "°"
                                color: AppTheme.Theme.textSecondary
                                font.pixelSize: 12
                            }
                        }

                        GridLayout {
                            Layout.columnSpan: root.width < 560 ? 2 : 1
                            Layout.fillWidth: true
                            columns: root.width < 560 ? 3 : 2
                            rowSpacing: 12
                            columnSpacing: 14

                            WeatherMetric {
                                Layout.fillWidth: true
                                icon: "💧"
                                label: "Humidity"
                                value: (weatherController.current.humidity || 0) + "%"
                            }

                            WeatherMetric {
                                Layout.fillWidth: true
                                icon: "🌧"
                                label: "Rain now"
                                value: (weatherController.current.precipitation || 0) + " in"
                            }

                            WeatherMetric {
                                Layout.fillWidth: true
                                icon: "💨"
                                label: "Wind"
                                value: (weatherController.current.windSpeed || 0) + " mph"
                            }
                        }
                    }
                }

                Text {
                    text: "Next hours"
                    color: AppTheme.Theme.textPrimary
                    font.pixelSize: 17
                    font.bold: true
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 116
                    model: weatherController.hourly
                    orientation: ListView.Horizontal
                    spacing: 8
                    clip: true
                    flickableDirection: Flickable.HorizontalFlick

                    ScrollBar.horizontal: ScrollBar {
                        policy: ScrollBar.AsNeeded
                    }

                    delegate: Rectangle {
                            width: 72
                            height: 108
                            radius: 16
                            color: AppTheme.Theme.surface
                            border.width: 1
                            border.color: AppTheme.Theme.divider

                            ColumnLayout {
                                anchors.fill: parent
                                anchors.margins: 9
                                spacing: 5

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.time
                                    color: AppTheme.Theme.textSecondary
                                    font.pixelSize: 11
                                }

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.icon
                                    font.pixelSize: 22
                                }

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.temperature + "°"
                                    color: AppTheme.Theme.textPrimary
                                    font.pixelSize: 16
                                    font.bold: true
                                }

                                Text {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: modelData.precipitation + "%"
                                    color: AppTheme.Theme.accent
                                    font.pixelSize: 10
                            }
                        }
                    }
                }

                Text {
                    text: "7-day forecast"
                    color: AppTheme.Theme.textPrimary
                    font.pixelSize: 17
                    font.bold: true
                }

                Repeater {
                    model: weatherController.daily

                    delegate: Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 54
                        radius: 14
                        color: AppTheme.Theme.surface
                        border.width: 1
                        border.color: AppTheme.Theme.divider

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 16
                            anchors.rightMargin: 16
                            spacing: 14

                            Text {
                                Layout.preferredWidth: 54
                                text: modelData.day
                                color: AppTheme.Theme.textPrimary
                                font.pixelSize: 13
                                font.bold: true
                            }

                            Text {
                                text: modelData.icon
                                font.pixelSize: 21
                            }

                            Text {
                                Layout.fillWidth: true
                                text: modelData.description
                                color: AppTheme.Theme.textSecondary
                                font.pixelSize: 12
                                elide: Text.ElideRight
                            }

                            Text {
                                text: modelData.precipitation + "%"
                                color: AppTheme.Theme.accent
                                font.pixelSize: 12
                            }

                            Text {
                                Layout.preferredWidth: 70
                                horizontalAlignment: Text.AlignRight
                                text: modelData.high + "° / " + modelData.low + "°"
                                color: AppTheme.Theme.textPrimary
                                font.pixelSize: 13
                                font.bold: true
                            }
                        }
                    }
                }
            }
        }
    }

    AppDialog {
        id: locationDialog
        objectName: "weatherLocationDialog"
        width: Math.min(root.width - 24, 560)
        title: "Choose your city"
        icon: "⌖"
        subtitle: "The location is stored only on this device."

        ColumnLayout {
            width: parent.width
            spacing: 12

            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                TextField {
                    id: citySearchField
                    Layout.fillWidth: true
                    Layout.preferredHeight: 50
                    placeholderText: "City or postal code"
                    font.pixelSize: 16
                    color: AppTheme.Theme.textPrimary
                    background: Rectangle {
                        radius: 14
                        color: AppTheme.Theme.canvas
                        border.width: 1
                        border.color: AppTheme.Theme.divider
                    }
                    onAccepted: weatherController.search(text)
                }

                ActionButton {
                    text: "Search"
                    primary: true
                    enabled: citySearchField.text.trim().length > 0
                             && !weatherController.busy
                    onClicked: weatherController.search(citySearchField.text)
                }
            }

            Text {
                Layout.fillWidth: true
                visible: weatherController.status.length > 0
                text: weatherController.status
                color: AppTheme.Theme.textSecondary
                font.pixelSize: 12
                wrapMode: Text.WordWrap
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(
                    root.height - 360,
                    240
                )
                clip: true
                ScrollBar.vertical.policy: ScrollBar.AsNeeded

                ColumnLayout {
                    width: parent.availableWidth
                    spacing: 8

                    Repeater {
                        model: weatherController.searchResults

                        delegate: ActionButton {
                            Layout.fillWidth: true
                            text: modelData.displayName
                            onClicked: {
                                weatherController.selectLocation(
                                    modelData.latitude,
                                    modelData.longitude,
                                    modelData.displayName
                                )
                                locationDialog.accept()
                            }
                        }
                    }
                }
            }
        }

        footer: Item {
            implicitHeight: 52

            ActionButton {
                anchors.right: parent.right
                anchors.rightMargin: 24
                anchors.verticalCenter: parent.verticalCenter
                text: "Cancel"
                onClicked: locationDialog.reject()
            }
        }
    }
}

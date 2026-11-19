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
        anchors.margins: 24
        spacing: 16

        RowLayout {
            Layout.fillWidth: true

            ColumnLayout {
                spacing: 3

                Text {
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
            visible: weatherController.hasLocation
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            ColumnLayout {
                width: parent.width
                spacing: 14

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 158
                    radius: AppTheme.Theme.radiusLarge
                    color: AppTheme.Theme.surface
                    border.width: 1
                    border.color: AppTheme.Theme.divider

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 20

                        Text {
                            text: weatherController.current.icon || "🌡"
                            font.pixelSize: 54
                        }

                        ColumnLayout {
                            Layout.preferredWidth: 150
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

                        Rectangle {
                            width: 1
                            Layout.fillHeight: true
                            color: AppTheme.Theme.divider
                        }

                        GridLayout {
                            Layout.fillWidth: true
                            columns: 2
                            rowSpacing: 12
                            columnSpacing: 24

                            WeatherMetric {
                                icon: "💧"
                                label: "Humidity"
                                value: (weatherController.current.humidity || 0) + "%"
                            }

                            WeatherMetric {
                                icon: "🌧"
                                label: "Rain now"
                                value: (weatherController.current.precipitation || 0) + " in"
                            }

                            WeatherMetric {
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

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Repeater {
                        model: weatherController.hourly

                        delegate: Rectangle {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 62
                            Layout.preferredHeight: 108
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
        anchors.centerIn: parent
        width: Math.min(root.width - 40, 560)
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

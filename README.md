# Swell Forecast

<p align="center">
  <img src="https://raw.githubusercontent.com/mrvautin/hacs-beach-swell-forecast/refs/heads/main/assets/logo.png" width="150px" />
</p>

This project provides a Home Assistant HACS integration to display a 7 day forecast for beach swells using [Surfline](https://www.surfline.com) data.

## Features

A sensor is created with forecasts the next 7 days with data like: 

- `Probability` = Percentage probability/accuracy
- `SurfMinFt` = Minimum surf height in feet 
- `SurfMaxFt` = Maximum surf height in feet 
- `SurfMinM` = Minimum surf height in meters 
- `SurfMaxM` = Maximum surf height in meters 
- `SurfPower` = The power of the swell
- `OptimalScore` = The wave score
- `HumanRelation` = The human relation measurement
- `ForecastDate` = The date of the forecast

## Installation

- In `HACS` > `3 dots` > `Custom Repositories`.
- In `Repository` add: `https://github.com/mrvautin/hacs-beach-swell-forecast`
- In `Type` select `Integration`
- Click `Add`

Once installed select `Settings` > `Devices and services` > `ADD INTEGRATION` > Search for `Swell Forecast`

In `Swell location name` enter a name which is appropriate to the location - `Southport SA, Australia`. 

> Note: it will be used to name the sensors 

In `Swell location latitude` you will need to latitude value for your Swell. 
In `Swell location longitude` you will need to longitude value for your Swell. 

In Google Maps, right click the beach location, select the latitude and longitude menu to copy to your clipboard.

<p align="center">
  <img src="https://raw.githubusercontent.com/mrvautin/hacs-beach-swell-forecast/refs/heads/main/assets/google-maps.png" width="450px" />
</p>

## Usage

There are many ways to display the swell data. The best way is to use the [Lovelace Swell Forecast Card](https://github.com/mrvautin/lovelace-swell-forecast-card). 

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# Football Predictions for Bundesliga ({{ date_today }})

> Disclaimer: The information provided is for informational purposes only and
> should not be construed as legal, financial, or professional advice.
> Gambling involves inherent risks, and individuals should exercise caution.
> If you encounter issues related to gambling, we recommend contacting the
> Centraal Register Uitsluiting Kansspelen authority in the Netherlands for
> assistance and support.

![https://kansspelautoriteit.nl/publish/pages/10841/ksa-logo_bigger-01.svg](https://kansspelautoriteit.nl/publish/pages/10841/ksa-logo_bigger-01.svg)
[Centraal Register Uitsluiting Kansspelen](https://cruksregister.nl/)

## Predictions
| Match  | Date | Win |
| ------------- | ------------- | ------------- |
{% for match in matches -%}
| {{ match.info_team_x }} vs {{ match.info_opponent_x }} | {{ match.info_date.strftime('%Y-%m-%d') }} | {{ match.info_venue_x }} |
{% endfor %}


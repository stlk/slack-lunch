# Slack lunch menu slash command

Uses Zomato and OpenCage Geocoder APIs. Build using Flask, deployed to now.sh.

### Development

#### Using now dev command

```bash
now dev
```

#### Using Flask dev

Configure your `.env` file and set `FLASK_APP` to the file you want to run.

```bash
pipenv install
pipenv run dev
```

### Tests

```bash
pipenv run pytest
```

### Deployment

```bash
# Add API keys
now secrets add ZOMATO_API_KEY your-secret-key
now secrets add OPENCAGEDATA_API_KEY your-secret-key

# Deploy
now
```
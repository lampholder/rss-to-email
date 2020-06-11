docker run --env-file env.file -v {$PWD}/state/:/opt/app/state/ rss-to-email

```
FEED_URL=https://example.com
BASIC_AUTH_USERNAME=bob
BASIC_AUTH_PASSWORD=bobisgreat
FROM_EMAIL_ADDRESS=noreply@example.com
TO_EMAIL_ADDRESS=me@example.com
SES_AWS_ACCESS_KEY_ID=KEYIDKEYID
SES_AWS_SECRET_ACCESS_KEY=SECRETKEYSECRETKEY
SES_AWS_REGION_NAME=eu-west-2
```

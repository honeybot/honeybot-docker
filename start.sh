#!/bin/bash

service redis-server restart
echo -e "HG_KEY=$HG_KEY\nHG_HOST=$HG_HOST\nHB_ID=$HB_ID\nHB_GROUPID=$HB_GROUPID\n* * * * * root /usr/bin/python3 /opt/client.py\n* * * * * root /usr/bin/python3 /opt/update.py" > /etc/cron.d/sync-job
chmod +x /etc/cron.d/sync-job
crontab /etc/cron.d/sync-job
touch /etc/openresty/ssl.conf
HG_KEY=$HG_KEY HG_HOST=$HG_HOST HB_ID=$HB_ID HB_GROUPID=$HB_GROUPID /usr/bin/python3 /opt/update.py
service openresty restart
if [[ ! -z "${SSL_HOST// }" ]]; then
  /opt/certbot/certbot-auto certonly --noninteractive --email admin@$SSL_HOST --agree-tos --webroot -w /usr/local/openresty/nginx/html -d $SSL_HOST
  echo -e "listen 443 ssl;\nssl_certificate /etc/letsencrypt/live/$SSL_HOST/fullchain.pem;\nssl_certificate_key /etc/letsencrypt/live/$SSL_HOST/privkey.pem;" > /etc/openresty/ssl.conf
  service openresty restart
  echo "0 2 28 * * /opt/certbot/certbot-auto renew --quiet && service openresty reload >/dev/null 2>&1" >> /etc/cron.d/letsencrypt
  crontab /etc/cron.d/letsencrypt
fi
while true
do
    cron -f
done

FROM node:lts AS builder

RUN npm install --legacy-peer-deps

RUN npm run build

FROM nginx:stable

COPY ./compose/nginx-proxy/nginx.conf.template /etc/nginx/templates/nginx.conf.template

CMD ["nginx","-g","daemon off;"]

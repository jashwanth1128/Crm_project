# Build Stage
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
# Use legacy peer deps purely to get past the conflicts
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run build

# Production Stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
# React Router support for Nginx
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Dockerfile для фронтенда (React)
FROM node:23-alpine

WORKDIR /app

COPY ./vikka/package*.json ./

RUN npm install

COPY ./vikka .

RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
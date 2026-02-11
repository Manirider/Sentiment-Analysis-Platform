FROM node:20

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install
# Rebuild esbuild to ensure correct binary for linux/amd64
RUN npm rebuild esbuild

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

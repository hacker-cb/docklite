const express = require('express');
const app = express();
const port = 3000;

app.get('/', (req, res) => {
  res.json({
    message: 'Hello World from Express!',
    framework: 'Express'
  });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.get('/info', (req, res) => {
  res.json({
    runtime: 'Node.js',
    version: process.version
  });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Express app listening on port ${port}`);
});


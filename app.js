import express from 'express';
import dotenv from 'dotenv';
import apiRouter from './routes/apiRouter.js';
dotenv.config({
    quiet: true
});

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api/", apiRouter);

app.get('/', (req, res) => {
    return res.json({
        success: true,
        status: "success",
        statusCode: 200,
        message: "Backend is running successfully"
    });
});

app.listen(PORT, () => {
    return console.log(`Server is running on http://localhost:${PORT}`);
});

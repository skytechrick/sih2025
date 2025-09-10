import multer from 'multer';
import path from 'path';

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function (req, file, cb) {
        cb(null, Date.now() + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });

export const handleFileUpload = (req, res, next) => {
    upload.single('file')(req, res, (err) => {
        if (err) {
            return res.status(500).send('Error uploading file: ' + err.message);
        }

        if (req.file) {
            const varFile = req.file;

            req.varFile = varFile;

            next();
        } else {
            res.status(400).send('No file uploaded.');
        }
    });
};

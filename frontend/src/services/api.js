import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const processImages = async (files, prompt) => {

    const formData = new FormData();

    formData.append(
        "prompt",
        prompt
    );

    files.forEach((file) => {

        formData.append(
            "files",
            file
        );

    });


    const response = await axios.post(
        `${API_URL}/agent`,
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data"
            }
        }
    );


    return response.data;
};
import { useRef } from "react";

function UploadZone({ files, setFiles }) {
  const inputRef = useRef(null);

  const addFiles = (selectedFiles) => {
    const imageFiles = Array.from(selectedFiles).filter((file) =>
      file.type.startsWith("image/")
    );

    if (imageFiles.length === 0) {
      alert("Please select image files only.");
      return;
    }

    setFiles((currentFiles) => [
      ...currentFiles,
      ...imageFiles,
    ]);
  };

  const handleInputChange = (event) => {
    addFiles(event.target.files);

    // Allow selecting the same file again
    event.target.value = "";
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();

    addFiles(event.dataTransfer.files);
  };

  const removeFile = (index) => {
    setFiles((currentFiles) =>
      currentFiles.filter((_, fileIndex) => fileIndex !== index)
    );
  };

  const clearFiles = () => {
    setFiles([]);
  };

  return (
    <div className="upload-section">

      <div
        className="upload-zone"
        onDragOver={(event) => event.preventDefault()}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <div className="upload-icon">
          ↑
        </div>

        <h3>
          Drop your images here
        </h3>

        <p>
          or click to browse from your device
        </p>

        <span>
          JPG, JPEG, PNG, WEBP, AVIF and more
        </span>

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          onChange={handleInputChange}
          hidden
        />
      </div>


      {files.length > 0 && (
        <div className="selected-files">

          <div className="files-header">

            <h3>
              Selected Images ({files.length})
            </h3>

            <button
              type="button"
              className="clear-button"
              onClick={clearFiles}
            >
              Clear all
            </button>

          </div>


          <div className="preview-grid">

            {files.map((file, index) => (

              <div
                className="preview-card"
                key={`${file.name}-${index}`}
              >

                <div className="preview-image-wrapper">

                  <img
                    src={URL.createObjectURL(file)}
                    alt={file.name}
                    className="preview-image"
                  />

                  <button
                    type="button"
                    className="remove-file"
                    onClick={(event) => {
                      event.stopPropagation();
                      removeFile(index);
                    }}
                    title="Remove image"
                  >
                    ×
                  </button>

                </div>

                <div className="preview-info">

                  <strong title={file.name}>
                    {file.name}
                  </strong>

                  <span>
                    {(file.size / 1024).toFixed(1)} KB
                  </span>

                </div>

              </div>

            ))}

          </div>

        </div>
      )}

    </div>
  );
}

export default UploadZone;
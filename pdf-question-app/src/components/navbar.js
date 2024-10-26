import React from 'react'


const NavBar = ({onUploadClick, documentName}) => {
    return (
        <nav>
            <div className="logo">
            </div>
            <div className="fileContainer">
                {documentName && <div className="filename">
                    <span className="file-icon"></span>
                    <div className="name">{documentName}</div>
                </div>}
                <button className="fileUpload" onClick={onUploadClick}>
                    <span className="add-icon"></span>
                    <div className="div">Upload PDF</div>
                    
                </button>
            </div>
        </nav>
    )
}

export default NavBar
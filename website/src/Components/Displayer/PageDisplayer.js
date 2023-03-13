import React from 'react';
import Box from '@mui/material/Box';

class PageDisplayer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            path: props.path,
            maxWidth: props.maxWidth || '150px'
        }
    }

    updatePath(path) {
        this.setState({path: path});
    }
    
    render() {
        return (
            <Box
                sx={{maxWidth: `${this.state.maxWidth}`, border: '1px solid #d9d9d9', boxShadow: 1, mr: '0.5rem'}}
            >
                <a
                    href={this.state.path}
                    target="_blank"
                    rel="noreferrer"
                >
                    <img
                        src={this.state.path}
                        alt={`Página de ${this.state.path}`}
                        style={{maxWidth: `${this.state.maxWidth}`}}
                    />
                </a>
            </Box>
        );
    }
}

export default PageDisplayer;
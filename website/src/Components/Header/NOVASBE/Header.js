import React from 'react';

import Box from '@mui/material/Box';
import Link from '@mui/material/Link';
import Button from '@mui/material/Button';
import HelpIcon from '@mui/icons-material/Help';

import logoNovaSBE from '../../../static/logoNovaSBE.png';

export default class Header extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            app: props.app,
            privateSession: props.privateSession,
            version: props.version
        }
    }

    render() {        
        return (
            <Box sx={{
                display: 'flex',
                flexDirection: 'row',
                justifyContent: 'space-between',
                ml: '1.5rem',
                mr: '1.5rem',
                mb: '1rem',
                mt: '1rem',
                zIndex: '100'
            }}>
                <Box sx={{display:'flex', flexDirection: 'row', alignItems: 'center'}}>  
                    <img src={logoNovaSBE} alt="logoNovaSBE" style={{paddingTop:'0.rem', paddingBottom: '0.5rem', marginRight:'2rem', height: '5rem', width: 'auto'}}/>
                    <Link
                        className="link"
                        sx={{
                            color: '#000000',
                            mr: '2rem', mt: '0.25rem', fontSize: '0.75rem'
                        }}
                        style={{textDecoration: 'none'}}
                        onClick={() => {
                                this.state.app.setState({fileSystemMode: true, editFileMode: false, filesChoice: [], algorithmChoice: [], configChoice: []})
                                this.state.app.redirectHome();                                                
                            }
                        }
                        underline="hover"
                    >
                        <h1>Início</h1>
                    </Link>
                    {
                        this.state.privateSession == null
                        ? <Link
                            className="link"
                            sx={{
                                color: '#000000',
                                mr: '0.05rem', mt: '0.25rem', fontSize: '0.75em'
                            }}
                            style={{textDecoration: 'none'}}
                            onClick={() => this.state.app.setState({fileSystemMode: false, editFileMode: false, filesChoice: [], algorithmChoice: [], configChoice: []})}
                            underline="hover"
                        >
                            <h1>Pesquisar</h1>
                        </Link>
                        : null
                    }
                </Box>

                <Box sx={{display: 'flex', flexDirection: 'row', alignItems: 'center'}}>
                    <p>{`Versão: ${this.state.version}`}</p>
                    <Button sx={{ml: '1.5rem', padding: '0rem', color: '#000000'}} 
                            onClick={() => window.open("https://docs.google.com/document/d/e/2PACX-1vR7BhM0haXd5CIyQatS22NrM44woFjChYCAaUAlqOjGAslLuF0TRPaMhjNW-dX8cxuaL86O5N_3mQMv/pub", '_blank')}
                    >
                        <HelpIcon sx={{mr: '0.3rem'}}>
                        </HelpIcon>
                        Ajuda
                    </Button>
                </Box>
            </Box>
        )
    }
}
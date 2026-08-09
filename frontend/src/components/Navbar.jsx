import { Link, NavLink } from 'react-router-dom';
import { USE_MOCK_API } from '../services/api';

export default function Navbar() {
  return <header className="navbar"><Link className="brand" to="/"><span className="brand-mark">◈</span><span>Inter<span>Vista</span></span></Link><nav><NavLink to="/">Overview</NavLink><NavLink to="/candidates">Candidates</NavLink></nav><div className="nav-status"><i /> AI interview engine <b>{USE_MOCK_API ? 'Mock fallback' : 'FastAPI connected'}</b></div></header>;
}

import { useDispatch } from 'react-redux';
import { logoutUser } from '../features/auth/authSlice';
import { useNavigate } from 'react-router-dom';
import "./Header.css"

export default function Header() {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    return (
        <div className='header'>
            <div className='links-container'>
                <div className='link left'>
                    <form action="/data">
                        <input type="submit" value="Просмотр данных" />
                    </form>
                </div>
                <div className='link'>
                    <form action="/forecast">
                        <input type="submit" value="Прогнозирование" />
                    </form>
                </div>
            </div>
            <div className='logout-container'>
                <button onClick={() => {
                            dispatch(logoutUser());
                            navigate('/login');
                        }}
                >
                    <svg xmlns="http://www.w3.org/2000/svg" width="40px" height="40px" viewBox="0 0 24 24" fill="none">
                        <path xmlns="http://www.w3.org/2000/svg" d="M2 6a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v2a1 1 0 1 1-2 0V6H4v12h9v-2a1 1 0 1 1 2 0v2a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6zm15.293 2.293a1 1 0 0 1 1.414 0l3 3a1 1 0 0 1 0 1.414l-3 3a1 1 0 0 1-1.414-1.414L18.586 13H9a1 1 0 1 1 0-2h9.586l-1.293-1.293a1 1 0 0 1 0-1.414z" fill="#0D0D0D"/>
                    </svg>
                </button>
            </div>

        </div>

    );
}
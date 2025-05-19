import { useState } from 'react';
import Header from '../../components/Header';
import api from '../../api/axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import "./Forecast.css"

export default function Forecast() {
    const [disease, setDisease] = useState('covid19');
    const [data, setData] = useState([]);
    const [horizon, setHorizon] = useState(1);
    
    const fetchData = async () => {
        try {
            const currentDate = new Date().toISOString().split('T')[0];
            const lastWindowDate = (new Date(new Date().setDate(new Date().getDate() - 99)).toISOString()).split('T')[0];
            console.log(horizon)
            const lastHorizonDate = (new Date(new Date().setDate(new Date().getDate() + +horizon - 1)).toISOString()).split('T')[0];
            console.log(lastWindowDate, currentDate, lastHorizonDate);

            api.get('/data', {
                params: { 
                    date_begin: lastWindowDate, 
                    date_end: currentDate, 
                    ds_name: disease 
                },
            }).then((response) => {
                const vec = response.data.map(t => t.value)

                console.log(vec)
                
                api.post('/predict',  {
                    X: vec
                }, {
                    params: {
                        date_begin: currentDate,
                        date_end: lastHorizonDate,
                        model: disease + '_model',
                    }
                }).then((response) => {
                    console.log(response.data)

                    const timeSeries = response.data.forecast.map((t, i) => ({ 
                        date: new Date(new Date().setDate(new Date().getDate() + i)).toISOString().split('T')[0], 
                        value: t
                    }))

                    setData(timeSeries);
                })
            })

        } catch (err) {
            console.error('Ошибка при получении данных:', err);
        }
    };
  
    return (
        <>
            <Header />
            <div className="container">
                <div className="items">
                    <div className="controls">
                      <div>
                        <label>Количество прогнозируемых дней: </label>
                        <input type="number" value={horizon} step="1" min="1" max="31" onChange={(e) => setHorizon(e.target.value)}/>
                      </div>
                      <select value={disease} onChange={(e) => setDisease(e.target.value)}>
                        <option value="covid19">Covid-19</option>
                        <option value="pneumania">Вирусная пневмония</option>
                      </select>
                      <div>
                        <button onClick={fetchData}>
                          Спрогнозировать
                        </button>
                      </div>

                    </div>

                    <div className="chart">
                      <ResponsiveContainer>
                        <LineChart data={data}>
                          <CartesianGrid stroke="#ccc" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Line type="monotone" dataKey="value" stroke="#8884d8" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </>
    );
}
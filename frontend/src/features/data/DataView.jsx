import { useState } from 'react';
import Header from '../../components/Header';
import api from '../../api/axios';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import "./DataView.css"

export default function DataView() {
    const [fromDate, setFromDate] = useState('');
    const [toDate, setToDate] = useState('');
    const [disease, setDisease] = useState('covid19');
    const [data, setData] = useState([]);
    
    const fetchData = async () => {
          try {
              const response = await api.get('/data', {
                  params: { date_begin: fromDate, date_end: toDate, ds_name: disease },
              });
              setData(response.data);
              console.log(response.data);
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
                        <label>С: </label>
                        <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)}/>
                      </div>
                      <div>
                        <label>По: </label>
                        <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)}/>
                      </div>
                      <select value={disease} onChange={(e) => setDisease(e.target.value)}>
                        <option value="covid19">Covid-19</option>
                        <option value="pneumania">Вирусная пневмония</option>
                      </select>
                      <button onClick={fetchData}>
                        Просмотр
                      </button>
                    </div>

                    <div className="chart">
                      <ResponsiveContainer>
                        <LineChart data={data}>
                          <CartesianGrid stroke="#ccc" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <Tooltip />
                          <Line type="monotone" dataKey="value" label="фыа" stroke="#8884d8" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </>
    );
}
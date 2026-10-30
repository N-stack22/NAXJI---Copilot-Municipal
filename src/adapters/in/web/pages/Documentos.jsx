import DocumentosInforme from "../components/DocumentosInforme";
import { puedeElaborar } from "../services/authService";
import "../styles/nuevoInforme.css";

export default function Documentos() {
  return <div className="nuevo-informe-page">
    <h1>Biblioteca de documentos autorizados</h1>
    <p>Incorpore referencias con autorización de uso y procese su texto para la recuperación documental.</p>
    <DocumentosInforme mostrarSeleccion={false} puedeCargar={puedeElaborar()} />
  </div>;
}

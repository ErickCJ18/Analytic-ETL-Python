# Diagrama de flujo del proceso ETL

Archivo con el diagrama en formato Mermaid. Pasa este archivo a una IA y pídele
"genera una imagen PNG/SVG de este diagrama Mermaid" (o ábrelo en
https://mermaid.live y exporta la imagen).

```mermaid
flowchart TD
    A([Inicio main.py]) --> B["get_engine() + SqlCleanRepository"]

    B --> F1{FASE 1<br/>Dimensiones en paralelo<br/>asyncio + threads}

    F1 --> C1[DimFecha]
    F1 --> C2[DimClasificacion]
    F1 --> C3[DimOrigen]
    F1 --> C4[DimCliente]
    F1 --> C5[DimProducto]

    C1 & C2 & C3 & C4 & C5 --> S1["1. Leer fuente CSV / generar"]
    S1 --> S2["2. Limpiar y validar"]
    S2 --> S3["3. Dedup contra tabla dim en BD"]
    S3 --> S4["4. Insertar con df.to_sql"]

    S4 --> D1{¿Fallo crítico?}
    D1 -- Sí --> E1["Log del error y continúa"]
    D1 -- No --> R1["Acumular resumen"]

    E1 --> F2{FASE 2<br/>Hechos en paralelo<br/>requieren dimensiones cargadas}
    R1 --> F2

    F2 --> H1[FactOpiniones]
    F2 --> H2[FactReviews]
    F2 --> H3[FactComments]

    H1 & H2 & H3 --> T1["1. Leer fuente CSV"]
    T1 --> T2["2. Limpiar y validar"]
    T2 --> T3{¿Tiene clasificador?}
    T3 -- Sí --> T4["3. Derivar clasificación"]
    T4 --> T5["4. Resolver surrogate keys contra dimensiones"]
    T3 -- No --> T5
    T5 --> T6["5. Dedup contra tabla fact en BD"]
    T6 --> T7["6. Insertar con df.to_sql"]

    T7 --> D2{¿Fallo crítico?}
    D2 -- Sí --> E1
    D2 -- No --> R2["Acumular resumen"]

    E1 --> G["Imprimir resumen final<br/>por entidad + totales"]
    R2 --> G
    G --> Z([Fin])
```

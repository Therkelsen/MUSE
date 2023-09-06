#ifndef RESSTRUCT_H
#define RESSTRUCT_H
#include <QWidget>

typedef struct _meterImpedance
{
    QString part = "A";
    float impModule[150][15] = { 0 };
    float impPhase[150][15] = { 0 };
}_meterImp;
#endif // RESSTRUCT_H

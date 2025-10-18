#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

/**
 * OPC-UA Client Plugin Module
 * Provides OPC-UA communication capabilities for Unreal Engine
 */
class FOPCUAClientModule : public IModuleInterface
{
public:
    /** IModuleInterface implementation */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

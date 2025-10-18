#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "OPCUAManager.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnOPCUAValueChanged, FString, NodeId, float, Value);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnOPCUABoolChanged, FString, NodeId, bool, Value);

/**
 * OPC-UA Manager
 * Handles connection and communication with OPC-UA server
 */
UCLASS(BlueprintType, Blueprintable)
class OPCUACLIENT_API UOPCUAManager : public UObject
{
    GENERATED_BODY()

public:
    UOPCUAManager();
    virtual ~UOPCUAManager();

    /**
     * Connect to OPC-UA server
     * @param ServerUrl Server endpoint URL (e.g., "opc.tcp://backend:4840")
     * @return True if connection successful
     */
    UFUNCTION(BlueprintCallable, Category = "OPC-UA")
    bool Connect(const FString& ServerUrl);

    /**
     * Disconnect from OPC-UA server
     */
    UFUNCTION(BlueprintCallable, Category = "OPC-UA")
    void Disconnect();

    /**
     * Check if connected to server
     */
    UFUNCTION(BlueprintPure, Category = "OPC-UA")
    bool IsConnected() const { return bIsConnected; }

    /**
     * Read float value from OPC-UA node
     * @param NodeId Node identifier (e.g., "ns=2;s=Motor1.Speed")
     * @param OutValue Retrieved value
     * @return True if read successful
     */
    UFUNCTION(BlueprintCallable, Category = "OPC-UA")
    bool ReadFloat(const FString& NodeId, float& OutValue);

    /**
     * Write float value to OPC-UA node
     * @param NodeId Node identifier
     * @param Value Value to write
     * @return True if write successful
     */
    UFUNCTION(BlueprintCallable, Category = "OPC-UA")
    bool WriteFloat(const FString& NodeId, float Value);

    /**
     * Read boolean value from OPC-UA node
     */
    UFUNCTION(BlueprintCallable, Category = "OPC-UA")
    bool ReadBool(const FString& NodeId, bool& OutValue);

    /**
     * Write boolean value to OPC-UA node
     */
    UFUNCTION(BlueprintCallable, Category = "OPC-UA")
    bool WriteBool(const FString& NodeId, bool Value);

    /**
     * Subscribe to node value changes
     * @param NodeId Node to monitor
     * @param UpdateInterval Monitoring interval in milliseconds
     */
    UFUNCTION(BlueprintCallable, Category = "OPC-UA")
    bool SubscribeToNode(const FString& NodeId, int32 UpdateInterval = 500);

    /** Event fired when subscribed float value changes */
    UPROPERTY(BlueprintAssignable, Category = "OPC-UA")
    FOnOPCUAValueChanged OnFloatValueChanged;

    /** Event fired when subscribed bool value changes */
    UPROPERTY(BlueprintAssignable, Category = "OPC-UA")
    FOnOPCUABoolChanged OnBoolValueChanged;

    /**
     * Tick function for processing OPC-UA callbacks
     * Call this from Actor Tick or Timer
     */
    UFUNCTION(BlueprintCallable, Category = "OPC-UA")
    void ProcessCallbacks();

protected:
    /** Current connection state */
    UPROPERTY(BlueprintReadOnly, Category = "OPC-UA")
    bool bIsConnected;

    /** Server endpoint URL */
    UPROPERTY(BlueprintReadOnly, Category = "OPC-UA")
    FString ServerUrl;

private:
    // OPC-UA client pointer (open62541)
    // void* ClientHandle; // Uncomment when integrating open62541

    /** Process incoming data from OPC-UA subscriptions */
    void ProcessSubscriptionData();
};

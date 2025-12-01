import { useState, useEffect, useRef } from "react";
import { StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { Magnetometer } from "expo-sensors";

export default function HomeScreen() {
    const [{ x, y, z }, setData] = useState({
        x: 0,
        y: 0,
        z: 0,
    });
    const [subscription, setSubscription] = useState(null);
    const [isWsOpen, setIsWsOpen] = useState(false);

    const dataRef = useRef("");
    const wsRef = useRef();
    const intervalRef = useRef();

    const _slow = () => Magnetometer.setUpdateInterval(1000);
    const _fast = () => Magnetometer.setUpdateInterval(16);

    const _subscribe = () => {
        setSubscription(
            Magnetometer.addListener((result) => {
                setData(result);
            })
        );
    };

    const _unsubscribe = () => {
        subscription && subscription.remove();
        setSubscription(null);
    };

    const connectToWs = () => {
        wsRef.current = new WebSocket("ws://192.168.1.25:9999");
        wsRef.current.onopen = () => {
            if (intervalRef.current) {
                clearInterval(intervalRef.current);
            }
            setIsWsOpen(true);
            intervalRef.current = setInterval(() => {
                sendData(wsRef.current);
            }, 10);
        };

        wsRef.current.onclose = () => {
            setIsWsOpen(false);
            clearInterval(intervalRef.current);
            setTimeout(function () {
                connectToWs();
            }, 1000);
        };

        wsRef.current.onerror = () => {
            setIsWsOpen(false);
            clearInterval(intervalRef.current);
            setTimeout(function () {
                connectToWs();
            }, 1000);
        };
    };

    const sendData = () => {
        wsRef.current.send(dataRef.current);
    };

    useEffect(() => {
        dataRef.current = JSON.stringify([x, y, z]);
    }, [x, y, z]);

    useEffect(() => {
        _subscribe();

        connectToWs();

        return () => {
            _unsubscribe();
        };
    }, []);

    if (!isWsOpen) {
        return (
            <View style={styles.container}>
                <Text>connecting to websocket...</Text>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            <Text style={styles.text}>Magnetometer:</Text>
            <Text style={styles.text}>x: {x}</Text>
            <Text style={styles.text}>y: {y}</Text>
            <Text style={styles.text}>z: {z}</Text>
            <View style={styles.buttonContainer}>
                <TouchableOpacity
                    onPress={subscription ? _unsubscribe : _subscribe}
                    style={styles.button}
                >
                    <Text>{subscription ? "On" : "Off"}</Text>
                </TouchableOpacity>
                <TouchableOpacity
                    onPress={_slow}
                    style={[styles.button, styles.middleButton]}
                >
                    <Text>Slow</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={_fast} style={styles.button}>
                    <Text>Fast</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: "center",
        paddingHorizontal: 10,
    },
    text: {
        textAlign: "center",
    },
    buttonContainer: {
        flexDirection: "row",
        alignItems: "stretch",
        marginTop: 15,
    },
    button: {
        flex: 1,
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "#eee",
        padding: 10,
    },
    middleButton: {
        borderLeftWidth: 1,
        borderRightWidth: 1,
        borderColor: "#ccc",
    },
});

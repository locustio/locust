package main

import boomer "github.com/myzhan/boomer"

import (
    "time"
    "net/http"
)


func now() int64 {
    return time.Now().UnixNano() / int64(time.Millisecond)
}


func test_http() {

    startTime := now()
    resp, err := http.Get("http://localhost:8080/")
    defer resp.Body.Close()
    endTime := now()

    if err != nil {
        boomer.Events.Publish("request_failure", "demo", "http", 0.0, err.Error())
    }else {
        boomer.Events.Publish("request_success", "demo", "http", float64(endTime - startTime), resp.ContentLength)
    }

}


func main() {

    task := &boomer.Task{
        Fn: test_http,
    }

    boomer.Run(task)

}

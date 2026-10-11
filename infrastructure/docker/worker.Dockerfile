FROM golang:1.24-alpine AS build
WORKDIR /src
COPY services/worker/ ./
RUN CGO_ENABLED=0 go build -trimpath -o /worker ./cmd/worker
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /worker /worker
ENTRYPOINT ["/worker"]

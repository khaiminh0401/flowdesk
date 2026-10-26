package io.flowdesk.shared.api;

/** Public diagnostic contract; never include deployment details or credentials. */
public record InfoResponse(String application, String stage) {}

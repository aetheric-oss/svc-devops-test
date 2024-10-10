//! REST API handlers for the devops-test service.

/// Public types needed to communicate with the REST interface
pub mod rest_types {
    include!("../../../../openapi/types.rs");
}

pub mod example;
pub mod health;

//! Re-export of used objects

pub use super::client as devops_test;
pub use super::service::Client as DevopsTestServiceClient;
pub use devops_test::DevopsTestClient;

pub use lib_common::grpc::Client;

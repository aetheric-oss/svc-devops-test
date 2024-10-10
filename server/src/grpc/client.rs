//! gRPC client helpers implementation
use tokio::sync::OnceCell;

use svc_assets_client_grpc::prelude::AssetsClient;
use svc_assets_client_grpc::prelude::Client as _;

pub(crate) static CLIENTS: OnceCell<GrpcClients> = OnceCell::const_new();

/// Returns CLIENTS, a GrpcClients object with default values.
/// Uses host and port configurations using a Config object generated from
/// environment variables.
/// Initializes CLIENTS if it hasn't been initialized yet.
pub async fn get_clients() -> &'static GrpcClients {
    CLIENTS
        .get_or_init(|| async move {
            let config = crate::Config::try_from_env().unwrap_or_default();
            GrpcClients::default(config)
        })
        .await
}

/// Struct to hold all gRPC client connections
#[derive(Clone, Debug)]
pub struct GrpcClients {
    /// svc-assets gRPC client handle
    pub assets: AssetsClient,
}

impl GrpcClients {
    /// Create new GrpcClients with defaults
    pub fn default(config: crate::Config) -> Self {
        GrpcClients {
            assets: AssetsClient::new_client(
                &config.assets_host_grpc,
                config.assets_port_grpc,
                "assets",
            ),
        }
    }
}

#[cfg(test)]
mod tests {
    use svc_assets_client_grpc::prelude::Client;

    use super::*;

    #[tokio::test]
    async fn test_grpc_clients_default() {
        lib_common::logger::get_log_handle().await;
        ut_info!("start");

        let config = crate::Config::default();
        let clients = GrpcClients::default(config);

        let assets = clients.assets;
        ut_debug!("assets: {:?}", assets);
        assert_eq!(assets.get_name(), "assets");

        ut_info!("success");
    }

    #[tokio::test]
    async fn test_get_clients() {
        lib_common::logger::get_log_handle().await;
        ut_info!("start");

        let clients = get_clients().await;

        ut_debug!("assets: {:?}", clients.assets);
        assert_eq!(clients.assets.get_name(), "assets");

        ut_info!("success");
    }
}

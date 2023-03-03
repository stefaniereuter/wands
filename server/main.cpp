#include "crow_all.h"

#include <adios2.h>
#include <H5Cpp.h>
#include <numeric>

crow::response ping() {
    crow::json::wvalue msg;
    msg["api"] = "wands";
    msg["version"] = "0.1";
    msg["endpoints"][0] = "/data";
    return msg;
}

template <typename T>
crow::logger& operator<<(crow::logger& out, const std::vector<T>& vec) {
    out << "[";
    const char* delim = "";
    const int max = 10;
    int i = 0;
    for (const auto& el : vec) {
        if (i == max) {
            out << delim << "...";
            break;
        }
        out << delim << el;
        delim = ", ";
        ++i;
    }
    out << "]";
    return out;
}

static std::vector<std::thread> threads;

template <typename T>
void send_data(int port, const std::string& signal, const std::vector<T>& data, const std::vector<hsize_t>& dims) {
    adios2::ADIOS adios;
    adios2::IO io = adios.DeclareIO("wands");
    io.SetEngine("DataMan");
    io.SetParameters({{"IPAddress", "127.0.0.1"},
                      {"Port", std::to_string(port)},
                      {"Timeout", "5"},
                      {"RendezvousReaderCount", "1"}});

    auto engine = io.Open("", adios2::Mode::Write);
    io.DefineAttribute("name", signal);

    adios2::Dims shape;
    std::copy(dims.begin(), dims.end(), std::back_inserter(shape));
    adios2::Dims start;
    start.resize(shape.size(), 0);
    adios2::Dims count;
    std::copy(dims.begin(), dims.end(), std::back_inserter(count));

    auto floatVar = io.DefineVariable<T>(signal, shape, start, count);
    engine.BeginStep();
    engine.Put(floatVar, data.data());
    engine.EndStep();

    engine.Close();
}

crow::response data(const crow::request& req) {

    crow::logger::setLogLevel(crow::LogLevel::Debug);
    auto data = crow::json::load(req.body);

    std::string uri_string;
    std::vector<std::string> signal_list;

    // POST data
    // - uri [STRING]
    // - signals [LIST]

    if (data.has("uri")) {
        auto& uri = data["uri"];
        if (uri.t() != crow::json::type::String) {
            auto msg = crow::json::wvalue({{"error", "uri must be a string"}});
            return { crow::status::BAD_REQUEST, msg };
        }
        uri_string = uri.s();
    } else {
        auto msg = crow::json::wvalue({{"error", "uri not found in POST data"}});
        return { crow::status::BAD_REQUEST, msg };
    }

    if (data.has("signals")) {
        auto& signals = data["signals"];
        if (signals.t() != crow::json::type::List) {
            auto msg = crow::json::wvalue({{"error", "signals must be a list of strings"}});
            return { crow::status::BAD_REQUEST, msg };
        }
        for (auto& signal : signals) {
            if (signal.t() != crow::json::type::String) {
                auto msg = crow::json::wvalue({{"error", "signals must be a list of strings"}});
                return { crow::status::BAD_REQUEST, msg };
            }
            signal_list.push_back(signal.s());
        }
    } else {
        auto msg = crow::json::wvalue({{"error", "signals not found in POST data"}});
        return { crow::status::BAD_REQUEST, msg };
    }

    // 1. Find file

    try {
        H5::H5File hdf5("/Users/jhollocombe/CLionProjects/wands/server/" + uri_string, H5F_ACC_RDONLY);

        for (auto& signal : signal_list) {
            CROW_LOG_DEBUG << "signal = " << signal;
            try {
                auto dset = hdf5.openDataSet(signal);
                auto type_class = dset.getTypeClass();
                auto dspace = dset.getSpace();
                CROW_LOG_DEBUG << "type_class = " << type_class;

                hsize_t rank;
                rank = dspace.getSimpleExtentNdims();
                CROW_LOG_DEBUG << "rank = " << rank;

                std::vector<hsize_t> dims;
                dims.resize(rank);
                dspace.getSimpleExtentDims(dims.data(), nullptr);
                CROW_LOG_DEBUG << "dims = " << dims;

                auto sz = std::accumulate(dims.begin(), dims.end(), 1, std::multiplies<>());

                if (type_class == H5T_FLOAT) {
                    auto flt_type = dset.getFloatType();
                    auto type_size = flt_type.getSize();

                    if (type_size == 4) {
                        std::vector<float> result;
                        result.resize(sz);
                        dset.read(result.data(), H5::PredType::NATIVE_FLOAT, H5S_ALL, H5S_ALL);
                        CROW_LOG_DEBUG << "data = " << result;

                        threads.emplace_back(send_data<float>, 8081, signal, result, dims);
                    } else if (type_size == 8) {
                        std::vector<double> result;
                        result.resize(sz);
                        dset.read(result.data(), H5::PredType::NATIVE_DOUBLE, H5S_ALL, H5S_ALL);
                        CROW_LOG_DEBUG << "data = " << result;

                        threads.emplace_back(send_data<double>, 8081, signal, result, dims);
                    }
                }
            } catch (H5::FileIException& ex) {
                auto msg = crow::json::wvalue({{"error", "signal '" + signal + "' not found"}});
                return { crow::status::NOT_FOUND, msg };
            }
        }
    } catch (H5::FileIException& ex) {
        auto msg = crow::json::wvalue({{"error", "file not found"}});
        return { crow::status::NOT_FOUND, msg };
    } catch (H5::Exception& ex) {
        auto msg = crow::json::wvalue({{"error", ex.getDetailMsg()}});
        return { crow::status::INTERNAL_SERVER_ERROR, msg };
    }

    // 2. Find signals in file
    // 3. Open ADIOS socket
    // 4. Put signal data onto socket
    // 5. Return ADIOS port to client

    crow::json::wvalue msg;
    msg["port"] = 8081;

    // RETURN
    // 200 - all good
    // { port: <ADIOS_PORT> }

    // 400 - bad POST message etc.
    // { error: <ERROR> }

    // 404 - uri or signal not found
    // { error: <ERROR> }

    // 500 - unexpected errors
    // { error: <ERROR> }

    return msg;
}

int main()
{
    crow::SimpleApp app;

    CROW_ROUTE(app, "/")(ping);
    CROW_ROUTE(app, "/data").methods("POST"_method)(data);

    app.port(8080).run();
    for (auto& thread : threads) {
        thread.join();
    }
    return 0;
}
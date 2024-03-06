#include "crow_all.h"

#include <adios2.h>
#include <H5Cpp.h>
#include <numeric>
#include <algorithm>

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

struct ReturnData {
    std::string signal;
    //currently can only send double reinstated once  https://github.com/ornladios/ADIOS2/issues/3538 is fixed
    //std::vector<char> data;
    // //begin bug hack
    std::vector<double> data;
    // //end bug hack
    std::vector<hsize_t> dims;
    std::string type;
};
struct Signal {
    std::string name;
    std::vector<hsize_t> shape;
    std::vector<hsize_t> offset;
};
std::string jsonTypeToString(crow::json::type t) {
    switch (t) {
        case crow::json::type::Null: return "Null";
        case crow::json::type::False: return "False";
        case crow::json::type::True: return "True";
        case crow::json::type::Number: return "Number";
        case crow::json::type::String: return "String";
        case crow::json::type::List: return "List";
        case crow::json::type::Object: return "Object";
        default: return "Unknown";
    }
}
static std::vector<std::thread> threads;

void send_data(int port, std::vector<ReturnData> return_data) {
    adios2::ADIOS adios;
    adios2::IO io = adios.DeclareIO("wands");
    io.SetEngine("DataMan");
    io.SetParameters({{"IPAddress", "127.0.0.1"},
                      {"Port", std::to_string(port)},
                      {"Timeout", "100"},
                      {"TransportMode","reliable"},
                      {"RendezvousReaderCount", "1"},
                      {"Threading","false"}});
    
    CROW_LOG_DEBUG << "initiating send ";

    auto engine = io.Open("WAN", adios2::Mode::Write);
    CROW_LOG_DEBUG << "ENGINE OPEN";
//    io.DefineAttribute("name", signal);

    engine.BeginStep();
    CROW_LOG_DEBUG << "Begin Step";
    for (const auto& item : return_data) {
        auto& dims = item.dims;

        adios2::Dims shape;
        std::copy(dims.begin(), dims.end(), std::back_inserter(shape));
        adios2::Dims start;
        start.resize(shape.size(), 0);
        adios2::Dims count;
        std::copy(dims.begin(), dims.end(), std::back_inserter(count));

        // // This will be the reinstated once https://github.com/ornladios/ADIOS2/issues/3538 is fixed
        // if (item.type == typeid(float).name()) {
        //     auto floatVar = io.DefineVariable<float>(item.signal, shape, start, count);
        //     auto buffer = reinterpret_cast<const float*>(item.data.data());
        //     //CROW_LOG_DEBUG << "data = " << buffer;
        //     engine.Put(floatVar, *buffer);
        // } else if (item.type == typeid(double).name()) {
        //     auto floatVar = io.DefineVariable<double>(item.signal, shape, start, count);
        //     auto buffer = reinterpret_cast<const double*>(item.data.data());
        //     //CROW_LOG_DEBUG << "data = " << buffer;
        //     engine.Put(floatVar, buffer);
        // }

        //begin bug hack

        auto floatVar = io.DefineVariable<double>(item.signal, shape, start, count);
        //CROW_LOG_DEBUG << "data = " << item.data.data();

        CROW_LOG_DEBUG << "before put";
        engine.Put(floatVar, item.data.data());
        CROW_LOG_DEBUG << "after put";
    
        //end bug hack
    }
    engine.EndStep();

    engine.Close();
}

crow::response data(const crow::request& req) {

    crow::logger::setLogLevel(crow::LogLevel::Debug);
    auto data = crow::json::load(req.body);

    std::string uri_string;
    std::vector<Signal> signal_list;    // POST data
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
        auto signals = data["signals"];
        std::cout<<"type "<<jsonTypeToString(signals.t())<<std::endl;
        if (!((signals.t() == crow::json::type::List) ||(signals.t() == crow::json::type::Object))) {
            auto msg = crow::json::wvalue({{"error", "signals must be a list of either strings or objects containing name, shape and offset"}});
            return { crow::status::BAD_REQUEST, msg };
        }
        // if (signal.t() != crow::json::type::Object || !signal.has("name") || !signal.has("shape") || !signal.has("offset")) {
        //         auto msg = crow::json::wvalue({{"error", "signals must be a list of objects containing name, shape and offset"}});
        //         return { crow::status::BAD_REQUEST, msg };
        // }
        std::cout<<"iterating over signals"<<std::endl;
        for (auto signal : signals) {
            std::cout<<"type "<<jsonTypeToString(signal.t())<<std::endl;

            if (!((signal.t() == crow::json::type::String) ||(signal.t() == crow::json::type::Object))) {
                auto msg = crow::json::wvalue({{"error", "signals must be a string of objects containing name, shape and offset"}});
                return { crow::status::BAD_REQUEST, msg };
            }
            std::cout<<"line 161"<<std::endl;
            Signal s;
            std::cout<<"line 163"<<std::endl;
            std::cout<<"type "<<jsonTypeToString(signal["name"].t())<<std::endl;

            s.name = signal["name"].s();
            std::cout<<"line 165"<<std::endl;
            std::cout<<"Name"<<s.name<<" ";
            for (auto& num: signal["shape"]){
                s.shape.push_back(num.u());
                std::cout<<"shape: ";
                for(auto i:s.shape) std::cout<<i<<" ";
                //std::ranges::copy(s.shape,std::ostream_iterator<hsize_t>(std::cout," "));
            }
            for (auto& num : signal["offset"]) {
                s.offset.push_back(num.u());
                std::cout<<"offset: ";
                //std::ranges::copy(s.shape,std::ostream_iterator<hsize_t>(std::cout," "));
                for(auto i:s.offset) std::cout<<i<<" ";

            }
            signal_list.push_back(s);
        }
    } else {
        auto msg = crow::json::wvalue({{"error", "signals not found in POST data"}});
        return { crow::status::BAD_REQUEST, msg };
    }

    
    // 1. Find file

    try {
       // H5::H5File hdf5("/home/sr2003/rds/rds-hpc-support-5mCMIDBOkPU/sr2003/UKAEA/Datafiles/" + uri_string, H5F_ACC_RDONLY);
        H5::H5File hdf5("/home/stefanie/work/adios/adiosnetwork/data/" + uri_string, H5F_ACC_RDONLY);
        //H5::H5File hdf5("/home/stefanie/work/adios/adiosnetwork/tests/test_data/" + uri_string, H5F_ACC_RDONLY);
        CROW_LOG_DEBUG << "file"<< hdf5.getFileName();
        std::vector<ReturnData> return_data;

        for (auto& signal : signal_list) {
            // auto data_signal = signal + "/data";
            // auto time_signal = signal + "/time";
            //get name
            // auto name = std::get<0>(signal);
            // std::vector<hsize_t> shape = std::get<1>(signal_tupel);
            // std::vector<hsize_t> offset= std::get<2>(signal_tupel);

            CROW_LOG_DEBUG << "signal = " << signal.name;
            try {
                auto data_dset = hdf5.openDataSet(signal.name);
                auto data_class = data_dset.getTypeClass();
                auto data_dspace = data_dset.getSpace();
                CROW_LOG_DEBUG << "data_class = " << data_class;

                //hsize_t data_rank = data_dspace.getSimpleExtentNdims();
                CROW_LOG_DEBUG << "offset = " << signal.offset;
                data_dspace.selectHyperslab(H5S_SELECT_SET, signal.shape.data(), signal.offset.data());
                // Create a DataSpace for the memory that will hold the read data
                H5::DataSpace mem_space(signal.shape.size(), signal.shape.data());
                // if (data_rank != 1) {
                //     return { crow::status::BAD_REQUEST, "invalid data rank" };
                // }

                //std::vector<hsize_t> data_dims;
                //data_dims.resize(data_rank);
                //data_dspace.getSimpleExtentDims(data_dims.data(), nullptr);
                CROW_LOG_DEBUG << "shape = " << signal.shape;

       
                // hsize_t len = data_dims[0];
                // std::vector<hsize_t> dims;
                // dims.resize(data_rank);
                // std::vector<hsize_t> dims = { 2, len };
                // Read the data
                std::vector<double> result;
                result.resize(std::accumulate(signal.shape.begin(), signal.shape.end(), 1, std::multiplies<hsize_t>()));
                data_dset.read(result.data(), H5::PredType::NATIVE_DOUBLE, mem_space, data_dspace);
                //(data_dims.begin(), data_dims.end(), 1, std::multiplies<>());

                if (data_class == H5T_FLOAT) {
                    auto flt_type = data_dset.getFloatType();
                    auto type_size = flt_type.getSize();

                //  //   will be reinstated once https://github.com/ornladios/ADIOS2/issues/3538 is fixed
                //     if (type_size == 4) {
                //         std::vector<char> result;
                //         result.resize(sz * sizeof(float));
                //         data_dset.read(&result[0], H5::PredType::NATIVE_FLOAT, H5S_ALL, H5S_ALL);
                //         time_dset.read(&result[len], H5::PredType::NATIVE_FLOAT, H5S_ALL, H5S_ALL);
                //         //CROW_LOG_DEBUG << "data = " << reinterpret_cast<const float>(result);

                //         return_data.emplace_back(ReturnData{signal, result, dims, typeid(float).name()});

                //     } else if (type_size == 8) {
                //         std::vector<char> result;
                //         result.resize(sz * sizeof(double));
                //         data_dset.read(&result[0], H5::PredType::NATIVE_DOUBLE, H5S_ALL, H5S_ALL);
                //         time_dset.read(&result[len], H5::PredType::NATIVE_DOUBLE, H5S_ALL, H5S_ALL);
                //         //CROW_LOG_DEBUG << "data = " << reinterpret_cast<const double>(result);

                //         return_data.emplace_back(ReturnData{signal, result, dims, typeid(double).name()});
                //     }
                    
                    // //begin bug hack
                    // std::vector<double> result;
                    // result.resize(sz);
                    // data_dset.read(result.data(), H5::PredType::NATIVE_DOUBLE, H5S_ALL, H5S_ALL);
                    // //time_dset.read(&result[len], H5::PredType::NATIVE_DOUBLE, H5S_ALL, H5S_ALL);
                    CROW_LOG_DEBUG << signal.name<< "data = " << result<<" size "<<result.size();

                    return_data.emplace_back(ReturnData{signal.name, result, signal.shape, typeid(double).name()});
                    //end bug hack
                }
            } catch (H5::FileIException& ex) {
                auto msg = crow::json::wvalue({{"error", "signal '" + signal.name + "' not found"}});
                return { crow::status::NOT_FOUND, msg };
            }
        }

        threads.emplace_back(send_data, 12345, std::move(return_data));

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
    msg["port"] = 12345;

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
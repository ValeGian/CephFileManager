#!flask/bin/python
import rados


def handle_request(request_type, parameter=""):

    cluster = rados.Rados(conffile='./ceph.conf')

    print("try to connect with: " + cluster.conf_get("mon host"))
    cluster.connect(10) #10 millisenconds of timeout
    pool = "data"

    response = ""
    if request_type == "add":
        response = add_object(pool, parameter, cluster)

    elif request_type == "get":
        response = get_object(pool, parameter, cluster)

    elif request_type == "get_objects_list":
        response = get_objects_list(pool, cluster)

    elif request_type == "delete":
        response = delete_object(pool, parameter, cluster)

    elif request_type == "get_status":
        response = get_status(pool, cluster)

    else:
        response = "invalid request"
    cluster.shutdown()

    return response


def add_object(pool, body, cluster):
    ret = ""
    try:
        io_context = cluster.open_ioctx(pool)
        succ = io_context.write_full(body['filename'], body['body'])
        if succ == 0:
            ret = "successfully added"
        else:
            ret = "unable to add the object"
    except Exception as e:
        print("error: {}".format(e))
        return "unable to add the object"
    finally:
        io_context.close()

    return ret


def get_object(pool, obj_id, cluster):
    object_to_return = ""
    try:
        io_context = cluster.open_ioctx(pool)
        object_to_return = io_context.read(obj_id)
    except Exception as e:
        print("error: {}".format(e))
        print("failed to get object " + obj_id)
        return  "unable to retrieve the object"
    finally:
        io_context.close()

    return object_to_return


def delete_object(pool, obj_id, cluster):
    ret = ""
    try:
        io_context = cluster.open_ioctx(pool)
        succ = io_context.remove_object(obj_id)
        if succ:
            ret = "successfully deleted"
        else:
            "unable to delete object"
    except Exception as e:
        print("error: {}".format(e))
        print("unable to remove object '{}' from pool '{}'\n".format(id, pool))
        return "unable to delete object " + obj_id
    finally:
        io_context.close()

    return ret


def get_objects_list(pool, cluster):
    obj_string = ""
    try:
        io_context = cluster.open_ioctx(pool)
        for obj in io_context.list_objects():
            obj_string += "{}\n".format(obj.key)
    except Exception as e:
        print("error: {}".format(e))
        print("unable to get object list from pool " + pool)
        return "unable to get object list"
    finally:
        if not obj_string:
            obj_string = "unable to get object list from pool " + pool
        io_context.close()

    return obj_string


def get_status(pool, cluster):
    cluster_status = "cluster Statistics:\n"
    try:
        io_context = cluster.open_ioctx(pool)
        stats = io_context.get_stats()

        for key, value in stats.items():
            cluster_status += str(key) + " : " + str(value) + "\n"

    except Exception as e:
        print("error: {}".format(e))
        cluster_status = "unable to get cluster status"

    return cluster_status